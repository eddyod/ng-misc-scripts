"""
Config File for parallel EC2 Processing of CZI Files
"""
NUM_INSTANCES = 125
S3_BUCKET = 'czi-process'
S3_CZI_DIR = 'DK39_uploaded'
SSH_KEY_LOC = 'czi-converter.pem'
S3_OUTPUT_DIR = 's3://czi-process/DK37_100_tif'

UPLOAD_DIR = None
DOWNLOAD_DIR = '.'
EMPTY_S3 = False
