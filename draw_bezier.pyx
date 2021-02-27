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
cimport numpy as np
cimport cython
cimport interpolation

from libc.math cimport floor, ceil, sqrt, fabs, sin, M_PI
from cython.parallel import prange

from cy_my_types cimport image_t

DEF NPOINTS=1000


@cython.boundscheck(False) # turn of bounds-checking for entire function
@cython.cdivision(True)
@cython.wraparound(False)
cdef void _draw_bezier(np.int8_t[:, :] canvas, float x0, float y0, float x1, float y1, float x2, float y2, float x3, float y3) nogil:
    cdef float bx, by, t
    cdef int i
    for i in range(NPOINTS):
        t = <float>i / <float>NPOINTS
        bx = (1-t)**3*x0 + 3*(1-t)*t**2*x1 + 3*(1-t)*(t**2)*x2 + t**3*x3
        by = (1-t)**3*y0 + 3*(1-t)*t**2*y1 + 3*(1-t)*(t**2)*y2 + t**3*y3

        canvas[<int>(by), <int>(bx)] = 1

def draw_bezier(np.int8_t[:, :] canvas, np.float64_t[:] points):
    _draw_bezier(canvas, points[0], points[1], points[2], points[3], points[4], points[5], points[6], points[7])




@cython.boundscheck(False) # turn of bounds-checking for entire function
@cython.cdivision(True)
@cython.wraparound(False)
def planify_curves(image_t[:, :, :] image, np.float64_t[:, :, :] curves):
    #  cdef np.ndarray[image_t, ndim=3] output
    cdef image_t[:, :, :] output
    cdef int ncurves = curves.shape[0]
    cdef int npoints = curves.shape[2]
    cdef int dx = image.shape[2]
    cdef int dy = image.shape[1]
    cdef int dz = image.shape[0]
    cdef int z, y, x

    output = np.zeros(shape=(ncurves, dz, npoints), dtype=np.int16)

    for z in prange(output.shape[0], nogil=True):
        for y in range(output.shape[1]):
            for x in range(output.shape[2]):
                output[z, y, x] = <image_t>interpolation.tricubicInterpolate(image, curves[z, 0, x], curves[z, 1, x], y)

    return np.asarray(output)
