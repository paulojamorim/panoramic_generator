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

import optparse as op
import pathlib
import sys

import h5py
import imageio
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from scipy import interpolate, ndimage
from scipy.optimize import minimize
from skimage import morphology

import bezier
import draw_bezier
import skeleton


def open_image(filename):
    with h5py.File(filename, "r") as f:
        return f["image"][()], f["spacing"][()]


def save_image(image, filename, spacing=(1.0, 1.0, 1.0)):
    image_nifti = nib.Nifti1Image(np.swapaxes(np.fliplr(image), 0, 2), None)
    image_nifti.header.set_zooms(spacing)
    image_nifti.header.set_dim_info(slice=0)
    nib.save(image_nifti, filename)


def diff_curves(control_points, skeleton_points):
    skx = skeleton_points[::2]
    sky = skeleton_points[1::2]

    bx, by = bezier.calc_bezier_curve(control_points, skx.shape[0])

    diff = ((bx - skx) ** 2 + (by - sky) ** 2).sum() ** 0.5

    #  global FRAME

    #  plt.clf()
    #  #  plt.figure(figsize=(20, 20))
    #  plt.xlim((-10, 700))
    #  plt.ylim((-10, 700))
    #  plt.plot(bx, by)
    #  plt.plot(skx, sky)
    #  plt.plot(control_points[::2], control_points[1::2])
    #  plt.scatter(control_points[::2], control_points[1::2])
    #  plt.savefig("/tmp/animation/%05d.png" % FRAME)
    #  FRAME += 1
    print(diff)
    return diff


def parse_comand_line():
    """
    Handle command line arguments.
    """
    usage = "usage: %prog [options] file.hdf5"
    parser = op.OptionParser(usage)

    # -d or --debug: print all pubsub messagessent
    parser.add_option(
        "-o", "--output", help="Output file (nifti)", default="sample.nii"
    )
    parser.add_option(
        "-d",
        "--distance",
        type="int",
        dest="distance",
        default=3,
        help="Distance between the curves",
    )
    parser.add_option(
        "-n",
        "--ncurves",
        type="int",
        dest="ncurves",
        default=10,
        help="Number of curves between and after the found curve",
    )
    parser.add_option(
        "-p",
        "--npoints",
        type="int",
        dest="npoints",
        default=500,
        help="Number of points (pixels) for each curve",
    )
    parser.add_option(
        "-g",
        "--nctrl_points",
        type="int",
        dest="nctrl_points",
        default=10,
        help="Number of bezier control points",
    )
    parser.add_option(
        "-t",
        "--threshold",
        type="int",
        dest="threshold",
        default=1500,
        help="Threshold used to determine the dental arcade",
    )
    parser.add_option(
        "-s",
        "--skeleton",
        dest="gen_skeleton",
        action="store_true",
        help="Generate skeleton image",
    )

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error("Incorrect number of arguments")

    filename = args[0]
    return filename, options


def main():
    filename, options = parse_comand_line()
    distance = options.distance
    ncurves = options.ncurves
    npoints = options.npoints
    nctrl_points = options.nctrl_points
    threshold = options.threshold
    output_filename = pathlib.Path(options.output).resolve()
    gen_skeleton = options.gen_skeleton

    if gen_skeleton:
        output_filename_skeleton = output_filename.parent.joinpath(
            output_filename.stem + "_skeleton" + output_filename.suffix
        )
        print(output_filename_skeleton)

    image, spacing = open_image(filename)
    skeleton_image, slice_number = skeleton.find_dental_arcade(image, threshold)
    skeleton_points = np.array(skeleton.img2points(skeleton_image), dtype=np.float64)

    skx, sky = skeleton.normalize_curve(skeleton_points, npoints)
    opt_skeleton_points = np.empty(shape=(npoints * 2), dtype=np.float64)
    opt_skeleton_points[::2] = skx
    opt_skeleton_points[1::2] = sky

    initial_points = np.random.random(nctrl_points * 2)

    res = minimize(
        diff_curves, initial_points, args=(opt_skeleton_points), method="SLSQP"
    )

    bx, by = bezier.calc_bezier_curve(res.x, npoints)
    curves = (
        bezier.calc_parallel_bezier_curves(
            res.x, distance=-distance, ncurves=ncurves, npoints=npoints
        )[::-1]
        + [(bx, by)]
        + bezier.calc_parallel_bezier_curves(
            res.x, distance=distance, ncurves=ncurves, npoints=npoints
        )
    )

    plt.imshow(image[slice_number], cmap="gray")
    plt.plot(skx, sky)
    for curve in curves:
        px, py = curve
        plt.plot(px, py)
    plt.axes().set_aspect("equal", "datalim")
    plt.show()

    #  print(res)

    panoramic_image = draw_bezier.planify_curves(image, np.array(curves))
    #  plt.imshow(panoramic_image.max(0), cmap="gray")
    #  plt.show()
    #  imageio.imsave("panoramic.png", panoramic_image)
    sx, sy, sz = spacing
    sx = (
        ((sx * bx[::2] - sx * bx[1::2]) ** 2 + (sy * by[::2] - sy * by[1::2]) ** 2)
        ** 0.5
    ).mean()
    save_image(panoramic_image, str(output_filename), spacing=(sx, sz, distance))

    if gen_skeleton:
        skx, sky = skeleton.normalize_curve(skeleton_points, npoints)
        skeleton_curves = (
            skeleton.calc_parallel_curves(
                skx, sky, distance=-distance, ncurves=ncurves
            )[::-1]
            + [(skx, sky)]
            + skeleton.calc_parallel_curves(
                skx, sky, distance=distance, ncurves=ncurves
            )[::-1]
        )

        plt.imshow(image[slice_number], cmap="gray")
        for curve in skeleton_curves:
            px, py = curve
            plt.plot(px, py)
        plt.axes().set_aspect("equal", "datalim")
        plt.show()

        panoramic_skeleton_image = draw_bezier.planify_curves(image, np.array(curves))

        sx, sy, sz = spacing
        sx = (
            (
                (sx * skx[::2] - sx * skx[1::2]) ** 2
                + (sy * sky[::2] - sy * sky[1::2]) ** 2
            )
            ** 0.5
        ).mean()
        save_image(
            panoramic_skeleton_image,
            str(output_filename_skeleton),
            spacing=(sx, sz, distance),
        )


if __name__ == "__main__":
    main()
