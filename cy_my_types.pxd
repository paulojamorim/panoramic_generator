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

#  ctypedef np.uint16_t image_t

ctypedef fused image_t:
    np.float64_t
    np.int16_t
    np.uint8_t

ctypedef np.uint8_t mask_t

ctypedef np.float32_t vertex_t
ctypedef np.float32_t normal_t

# To compile in windows 64
IF UNAME_MACHINE == 'AMD64':
    ctypedef np.int64_t vertex_id_t
ELSE:
    ctypedef np.int_t vertex_id_t
