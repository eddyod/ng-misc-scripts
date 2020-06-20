"""
Script to run processing of CZI Files
"""
import boto3
from instance_manage import EC2Instance
import threading
import paramiko
import logging
import time

launch_template_dict = {'LaunchTemplateId': "lt-055614c16e52565b4", 'Version': '1'}
ec2 = boto3.resource('ec2', region_name='us-west-1')
s3 = boto3.client('s3')

# inst = EC2Instance(ec2, launch_template_dict)
# inst.start_instance()
# in_s3 = 's3://czi-process/raw/2019_09_30__6906.czi'
# out_s3 = 's3://czi-process/test/'
# inst.process_image(in_s3, out_s3)
# inst.terminate_instance()

# =======================================================
NUM_INSTANCES = 5
S3_BUCKET = 'czi-process'
S3_CZI_DIR = 'DK39'
SSH_KEY_LOC = 'czi-converter.pem'

S3_OUTPUT_DIR = 's3://czi-process/DK39_tif'


# =======================================================

def run_command_on_ec2(host, command):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key = paramiko.RSAKey.from_private_key_file(SSH_KEY_LOC)

    with ssh_lock:
        ssh.connect(hostname=host, username="ubuntu", pkey=key)
        stdin, stdout, stderr = ssh.exec_command(command)
        stdin.flush()

    with output_lock:
        data = stdout.readlines()
        for line in data:
            print(line)


def setup_instance(host):
    try:
        run_command_on_ec2(host, 'rm -r ~/src && aws s3 cp --recursive s3://czi-process/src ~/src && echo "src files copied"')

    except Exception as e:
        logging.error(f"Exception: Setting up instance failed | {e}")


def process_image(host):

    if len(s3_file_list) > 0:
        try:
            image_loc_s3 = s3_file_list.pop(0)
            print(f"Processing S3 File {image_loc_s3}")

            command_list = ['rm -f ~/data/raw/*', 'rm -f ~/data/output/*', f'aws s3 cp {image_loc_s3} ~/data/raw/',
                            'echo "File Download Completed"',
                            'python ~/src/convert_all_files.py',
                            f'aws s3 cp --recursive ~/data/output/ {S3_OUTPUT_DIR}']
            command_string = ' && '.join(command_list)
            run_command_on_ec2(host, command_string)

        except Exception as e:
            logging.error(f"File: {image_loc_s3} \n Exception: {e}")


# ===============================================================================================

instance_list = []
instance_ips = []

s3_file_list = []

file_objs = s3.list_objects(Bucket=S3_BUCKET, Prefix=S3_CZI_DIR)

for obj in file_objs['Contents']:
    if obj['Key'].endswith('.czi'):
        s3_file_list.append(f's3://{S3_BUCKET}/{obj["Key"]}')

print(f"Number of Images to Process: {len(s3_file_list)}")
output_lock = threading.Lock()
ssh_lock = threading.Lock()

for i in range(0, NUM_INSTANCES):
    inst = EC2Instance(ec2, launch_template_dict)
    inst.start_instance()
    instance_list.append(inst)
    instance_ips.append(inst.public_dns)
    setup_instance(inst.public_dns)


print(f"Instances spun up: {str(instance_ips)}")

# GET IMAGES



# def process_image(host):
#
#     if len(s3_file_list) > 0:
#         try:
#             image_loc_s3 = s3_file_list.pop(0)
#             print(f"Processing S3 File {image_loc_s3}")
#
#             command_list = ['rm -f ~/data/raw/*', 'rm -f ~/data/output/*', f'aws s3 cp {image_loc_s3} ~/data/raw/',
#                             'echo "File Download Completed"',
#                             'python ~/src/convert_all_files.py',
#                             f'aws s3 cp --recursive ~/data/output/ {S3_OUTPUT_DIR}']
#             command_string = ' && '.join(command_list)
#             print("Running Command: " + command_string)
#             ssh = paramiko.SSHClient()
#             ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#             key = paramiko.RSAKey.from_private_key_file(SSH_KEY_LOC)
#             ssh.connect(hostname=host, username="ubuntu", pkey=key)
#             stdin, stdout, stderr = ssh.exec_command(command_string)
#             stdin.flush()
#
#             # with output_lock:
#             #     print(stdout.readlines())
#
#         except Exception as e:
#             logging.error(f"File: {image_loc_s3} \n Exception: {e}")


while len(s3_file_list) > 0:
    threads = []
    for h in instance_ips:
        t = threading.Thread(target=process_image, args=(h,))
        t.start()
        threads.append(t)
        time.sleep(4)

    for t in threads:
        t.join()

for inst in instance_list:
    inst.terminate_instance()

print("CZI Conversion process complete")
