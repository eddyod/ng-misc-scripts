"""
View a numpy 3D matrix using neuroglancer.
"""
from __future__ import print_function

import argparse
import numpy as np
import os
import neuroglancer

DOWNLOAD_DIR = '/home/s9jain/vol_fill'
LOCAL_FILE_NAME = 'MD585_full.npy'
LOCAL_FILE_LOC = os.path.join(DOWNLOAD_DIR, LOCAL_FILE_NAME)
FINAL_FILE_LOC = os.path.join(DOWNLOAD_DIR, 'MD585_full_filled.npy')

a = np.load(FINAL_FILE_LOC)
neuroglancer.set_server_bind_address(bind_port='33645')

viewer = neuroglancer.Viewer()
dimensions = neuroglancer.CoordinateSpace(
    names=['x', 'y', 'z'],
    units='nm',
    scales=[10, 10, 10])
with viewer.txn() as s:
    s.dimensions = dimensions
    s.layers.append(
        name='a',
        layer=neuroglancer.LocalVolume(
            data=a,
            dimensions=neuroglancer.CoordinateSpace(
                names=['z', 'y', 'x'],
                units=['um','um','um'],
                scales=[20, 5, 5]),
            voxel_offset=(0, 0, 0),
        ))

print(viewer)
a=1
