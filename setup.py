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

import os
import sys
from distutils.core import setup
from distutils.extension import Extension

import numpy
from Cython.Build import cythonize
from Cython.Distutils import build_ext

if sys.platform == 'darwin':
    unix_copt = ['-Xpreprocessor', '-fopenmp', '-lomp']
    unix_lopt = ['-Xpreprocessor', '-fopenmp', '-lomp']
else:
    unix_copt = ['-fopenmp',]
    unix_lopt = ['-fopenmp',]


copt = {"msvc": ["/openmp"], "mingw32": ["-fopenmp"], "unix": unix_copt}

lopt = {"mingw32": ["-fopenmp"], "unix": unix_lopt}


class build_ext_subclass(build_ext):
    def build_extensions(self):
        c = self.compiler.compiler_type
        print("Compiler", c)
        if c in copt:
            for e in self.extensions:
                e.extra_compile_args = copt[c]
        if c in lopt:
            for e in self.extensions:
                e.extra_link_args = lopt[c]
        for e in self.extensions:
            e.include_dirs = [numpy.get_include()]
        build_ext.build_extensions(self)


setup(
    cmdclass={"build_ext": build_ext_subclass},
    ext_modules=cythonize(
        [
            Extension(
                "draw_bezier",
                ["draw_bezier.pyx"],
            ),
            Extension(
                "interpolation",
                ["interpolation.pyx"],
            ),
        ]
    ),
)
