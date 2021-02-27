# Panoramic Generator
Source code from paper [Reconstruction of Panoramic Dental Images Through Bézier Function Optimization](https://doi.org/10.3389/fbioe.2020.00794)

## Prerequisites (Tested on Ubuntu 20.04):

`pip install h5py imageio matplotlib nibabel numpy scipy scikit-image Cython`

### Compile Cython code:

`python setup.py build_ext --inplace`

## Running

```
python panoramic_generator.py file.hdf5 [options]

Options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output=OUTPUT
                        Output file (nifti default is panoramic.nii)
  -d DISTANCE, --distance=DISTANCE
                        Distance between the curves
  -n NCURVES, --ncurves=NCURVES
                        Number of curves between and after the found curve
  -p NPOINTS, --npoints=NPOINTS
                        Number of points (pixels) for each curve
  -g NCTRL_POINTS, --nctrl_points=NCTRL_POINTS
                        Number of bezier control points
  -t THRESHOLD, --threshold=THRESHOLD
                        Threshold used to determine the dental arcade
  -s, --skeleton        Generate skeleton image

```

## How to generate .hdf5 file to input?

Download and install the [InVesalius](https://github.com/invesalius/invesalius3/releases/tag/v3.1.99994) software.

1. Open InVesalius

2. Import DICOM files or another medical file format

3. On Menubar. File -> Export Project

## How to view generated panoramics (.nii files)?

1. Open InVesalius

2. On Menubar. File -> Import other files -> NIfTI 1

3. Import your generated .nii file (default is panoramic.nii) and visualize.

## Citation

Amorim PHJ, Moraes TF, Silva JVL, Pedrini H and Ruben RB (2020) Reconstruction of Panoramic Dental Images Through Bézier Function Optimization. Front. Bioeng. Biotechnol. 8:794. doi: 10.3389/fbioe.2020.00794
