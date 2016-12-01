#!/usr/bin/python

# ============================================================================
#
# resamp_rho.py
#
# Resample spatial random effects
#
# Ghislain Vieilledent <ghislain.vieilledent@cirad.fr>
# November 2016
#
# ============================================================================

# =============================================
# Libraries
# =============================================

import numpy as np
from osgeo import gdal
import os


# =============================================
# resamp_rho
# =============================================


def resample_rho(rho, raster, output_file="output/rho.tif",
                 csize_orig=10, csize_new=1):

    # Region
    r = gdal.Open(raster)
    ncol = r.RasterXSize
    nrow = r.RasterYSize
    gt = r.GetGeoTransform()
    Xmin = gt[0]
    Xmax = gt[0]+gt[1]*ncol
    Ymin = gt[3]+gt[5]*nrow
    Ymax = gt[3]

    # Cell number from region
    csize_orig = csize_orig * 1000  # Transform km in m
    ncell_X = np.ceil((Xmax - Xmin) / csize_orig).astype(int)
    ncell_Y = np.ceil((Ymax - Ymin) / csize_orig).astype(int)

    # NumpyArray
    rho_arr = rho.reshape(ncell_Y, ncell_X)

    # Create .tif file
    dirname = os.path.dirname(output_file)
    filename = os.path.join(dirname, "rho_orig.tif")
    driver = gdal.GetDriverByName("GTiff")
    rho_R = driver.Create(filename, ncell_X, ncell_Y, 1, gdal.GDT_Float64)
    rho_R.SetProjection(r.GetProjection())
    gt = list(gt)
    gt[1] = csize_orig
    gt[5] = -csize_orig
    rho_R.SetGeoTransform(gt)

    # Write data
    rho_B = rho_R.GetRasterBand(1)
    rho_B.WriteArray(rho_arr)
    rho_B.FlushCache()
    rho_B.ComputeStatistics(False)
    rho_B = None
    del rho_R

    # Resample with interpolation
    command = "gdalwarp -overwrite -tr 1000 1000 -r bilinear " + filename + " " + output_file
    os.system(command)
    print("Spatial random effects resampled to file " + output_file)
    return (None)
