"""
This script takes as input a segmentation map represented as a numpy array and converts into a
precomputed volume to be shown on neuroglancer.
"""

import numpy as np
import pickle as pkl
import boto3

import os

import json
import pathlib
from neuroglancer_scripts.scripts import (generate_scales_info,
                                          slices_to_precomputed,
                                          compute_scales, volume_to_precomputed)
import nibabel as nib
import re
stack = 'MD594'
DOWNLOAD_DIR = '/home/s9jain/vol_fill'
LOCAL_FILE_NAME = f'{stack}_full.npy'

ni_out = os.path.join(DOWNLOAD_DIR, f'{stack}_filled.nii')
source_dir = os.path.join(DOWNLOAD_DIR, f'{stack}_full_filled.npy')
out_dir = os.path.join(DOWNLOAD_DIR,f'{stack}_filled_precomputed')

if not os.path.isdir(out_dir):
    os.mkdir(out_dir)

vol_m = np.load(source_dir)

vol_m = np.swapaxes(vol_m,0,2)
print(vol_m.shape)
vol_img = nib.Nifti1Image(vol_m, affine=np.array(\
      [[ 0.005,  0.,  0.,  0.],\
       [ 0.,   0.005,  0.,  0.],\
       [ 0.,  0.,  0.02,  0.],\
       [ 0.,  0.,  0.,  1.]]))
nib.save(vol_img, ni_out)

volume_to_precomputed.main(['', ni_out, out_dir, '--generate-info', '--no-gzip'])
with open(os.path.join(os.path.join(out_dir, 'info_fullres.json')), 'r') as info_file:
    info = json.load(info_file)

info["type"] = "segmentation"

with open(os.path.join(os.path.join(out_dir, 'info_fullres.json')), 'w') as info_file:
    json.dump(info, info_file)

generate_scales_info.main(['', os.path.join(out_dir, 'info_fullres.json'), '--encoding', 'compressed_segmentation',
                           out_dir, '--max-scales', '1', '--target-chunk-size', '128'])

volume_to_precomputed.main(['', ni_out, out_dir, '--flat', '--no-gzip'])
