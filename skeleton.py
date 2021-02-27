#--------------------------------------------------------------------------
# Software:     Panoramic generator from CT

# Comments:     This code is from paper: "Reconstruction of Panoramic 
#               Dental Images Through Bézier Function Optimization"
#               https://doi.org/10.3389/fbioe.2020.00794

# Copyright:    (C) 2019 - CTI Renato Archer

# Authors:      Paulo H. J. Amorim (paulo.amorim (at) cti.gov.br) 
#               Thiago F. Moraes (thiago.moraes (at) cti.gov.br)
#               Jorge V. L. Silva (jorge.silva (at) cti.gov.br)
#               Helio Pedrini (helio (at) ic.unicamp.br)
#               Rui B. Ruben (rui.ruben (at) ipleiria.pt)

# Homepage:     http://www.cti.gov.br/invesalius

# Contact:      invesalius@cti.gov.br

# License:      GNU - GPL 2 (LICENSE.txt/LICENCA.txt)
#---------------------------------------------------------------------------

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#---------------------------------------------------------------------------

import imageio
import numpy as np
from scipy import interpolate, ndimage
from skimage import morphology


def arcade_as_skeleton(image):
    image = image.astype(np.uint8)

    op = np.ones((30, 30))
    image = ndimage.morphology.binary_dilation(image, op)
    image = ndimage.gaussian_filter(image * 255, 2).astype(np.int8)

    image[image != 0] = 1.0
    image[image <= 0] = 0

    image = image.astype(np.int)

    imageio.imsave("image_bin.png", image * 255)

    image_labels = morphology.label(image)  # , background=0)#, neighbors=8)

    # Conta quantos pixeis tem em cada objeto
    labels = {}
    for y in range(image_labels.shape[0]):
        for x in range(image_labels.shape[1]):
            px = image_labels[y, x]
            if px != 0:
                if px in list(labels.keys()):
                    labels[px] += 1
                else:
                    labels[px] = 0

    big_value = max(labels.values())
    # Pega qual o label que contem mais pixeis
    for k in list(labels.keys()):
        if labels[k] == big_value:
            big_label = k

    # Apaga a regiao da imagem que nao e o maior objeto
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            px_l = image_labels[y, x]
            if px_l != big_label:
                image[y, x] = 0

    # pylab.imshow(image, cmap=pylab.cm.gray)
    # pylab.show()
    # pylab.imsave("./component.png", image)
    # Extrai o esqueleto do objeto

    image = morphology.skeletonize(image)
    # pylab.imsave("./skeleton.png", image)

    return image


def find_dental_arcade(image, threshold):
    bin_image = image >= threshold
    best_slice_number = bin_image.reshape(bin_image.shape[0], -1).sum(1).argmax()
    print("Best slice number", best_slice_number)
    best_slice = bin_image[best_slice_number]
    skeleton_image = arcade_as_skeleton(best_slice)
    return skeleton_image, best_slice_number


def img2points(img):
    bw_img = img * 1
    points = []
    for y in range(bw_img.shape[0]):
        for x in range(bw_img.shape[1]):
            if bw_img[y, x]:
                points.append((x, y))
                break
        if points:
            break

    xi, yi = points[-1]
    while True:
        xn, yn = points[-1]
        nexts = [
            (xn + i, yn + j)
            for i, j in (
                (+1, 0),
                (0, +1),
                (-1, 0),
                (0, -1),
                (+1, +1),
                (-1, +1),
                (-1, -1),
                (+1, -1),
            )
            if ((0 < xn + i < img.shape[1]) and (0 < yn + j < img.shape[0]))
        ]
        appended = False
        for x, y in nexts:
            if bw_img[y, x] == 1:
                bw_img[y, x] = 2
                points.append((x, y))
                appended = True
                break

        if not appended:
            return points


def normalize_curve(points, npoints):
    px = points[:, 0]
    py = points[:, 1]

    t = np.linspace(0, 1, len(points))
    fx = interpolate.CubicSpline(t, px)
    fy = interpolate.CubicSpline(t, py)

    nt = np.linspace(0, 1, npoints)
    npx = fx(nt)
    npy = fy(nt)

    return npx, npy


def calc_tangents(px, py, normalize=True):
    gx = np.gradient(px)
    gy = np.gradient(py)
    if normalize:
        size = (gx ** 2 + gy ** 2) ** 0.5
        gx /= size
        gy /= size
    return gx, gy


def calc_normals(px, py):
    tx, ty = calc_tangents(px, py, normalize=True)
    nx = tx * np.cos(np.pi / 2.0) - ty * np.sin(np.pi / 2.0)
    ny = tx * np.sin(np.pi / 2.0) + ty * np.cos(np.pi / 2.0)
    return nx, ny


def calc_parallel_curves(px, py, distance=1, ncurves=10):
    nx, ny = calc_normals(px, py)
    curves = []
    for i in range(1, ncurves + 1):
        ppx = i * distance * nx + px
        ppy = i * distance * ny + py
        curves.append((ppx, ppy))
    return curves
