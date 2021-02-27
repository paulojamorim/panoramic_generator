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

import numpy as np

import matplotlib.pyplot as plt

lut = [
    [1],
    [1, 1],
    [1, 2, 1],
    [1, 3, 3, 1],
    [1, 4, 6, 4, 1],
    [1, 5, 10, 10, 5, 1],
    [1, 6, 15, 20, 15, 6, 1],
]


def binomial(n, k):
    while n >= len(lut):
        s = len(lut)
        next_row = [1]
        for i in range(1, s):
            value = lut[-1][i - 1] + lut[-1][i]
            next_row.append(value)
        next_row.append(1)
        lut.append(next_row)
    return lut[n][k]


def bezier(n, t, w):
    sum = np.zeros_like(t)
    for k in range(n + 1):
        sum += w[k] * binomial(n, k) * (1 - t) ** (n - k) * t ** (k)
    return sum


def derivative_bezier(n, t, w):
    sum = np.zeros_like(t)
    k = n - 1
    for i in range(k + 1):
        sum += binomial(k, i) * (1 - t)**(k - i) * t**(i) * n * (w[i + 1] - w[i])
    return sum


def calc_tangents(control_points, npoints=1000, normalize_curve=True):
    degree = len(control_points) // 2 - 1
    t = np.linspace(0, 1, npoints)
    tx = derivative_bezier(degree, t, control_points[::2])
    ty = derivative_bezier(degree, t, control_points[1::2])
    if normalize_curve:
        d = (tx**2 + ty**2)**0.5
        tx = tx / d
        ty = ty / d
    return tx, ty


def calc_bezier_normals(control_points, npoints=1000):
    tx, ty = calc_tangents(control_points, npoints, normalize_curve=True)
    nx = tx * np.cos(np.pi/2.0) - ty * np.sin(np.pi/2.0)
    ny = tx * np.sin(np.pi/2.0) + ty * np.cos(np.pi/2.0)
    return nx, ny


def calc_parallel_bezier_curves(control_points, distance=1, ncurves=10, npoints=1000):
    bx, by = calc_bezier_curve(control_points, npoints)
    nx, ny = calc_bezier_normals(control_points, npoints)
    curves = []
    for i in range(1, ncurves + 1):
        px = i * distance * nx + bx
        py = i * distance * ny + by
        curves.append((px, py))
    return curves


def calc_bezier_curve(control_points, npoints=1000):
    degree = len(control_points) // 2 - 1
    t = np.linspace(0, 1, npoints)
    #  fx = np.vectorize(lambda x: bezier(degree, x, control_points[::2]))
    #  fy = np.vectorize(lambda x: bezier(degree, x, control_points[1::2]))
    x = bezier(degree, t, control_points[::2])
    y = bezier(degree, t, control_points[1::2])
    return x, y




def main():
    points = np.random.random(18)
    px, py = calc_bezier_curve(points)

    plt.plot(px, py)
    plt.plot(points[::2], points[1::2])
    plt.show()

    print(lut)



if __name__ == "__main__":
    main()
