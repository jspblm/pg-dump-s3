""" Database backup """

import subprocess
import datetime
import os
import sys
import gzip
import shutil

import boto3
import secrets

dump_name = secrets.DATABASE_DUMP_NAME
dump_name_gz = '%s.gz' % (dump_name,)
db_name = secrets.DATABASE_NAME
email_origin = secrets.EMAIL_ORIGIN
email_destination = secrets.EMAIL_DESTINATION

cwd = os.getcwd()

dump = subprocess.run(['pg_dump', '-d', db_name, '-f', dump_name],
                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

if dump.stdout:
    print('[ERROR]', dump.stdout)
    sys.exit(1)

# Compress file
with open('%s/%s' % (cwd, dump_name), 'rb') as f_in:
    with gzip.open('%s/%s' % (cwd, dump_name_gz), 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

s3 = boto3.client(
    's3',
    aws_access_key_id=secrets.ACCESS_KEY,
    aws_secret_access_key=secrets.SECRET_KEY
)

date = datetime.datetime.utcnow()

# Send the compressed file
s3_key = '%s-%s-UTC.sql.gz' % (db_name, date.strftime('%Y-%m-%dT%H%M'))
s3_result = s3.upload_file(dump_name_gz, secrets.BUCKET_NAME, s3_key)

# Send a confirmation email
ses = boto3.client(
    'ses',
    aws_access_key_id=secrets.ACCESS_KEY,
    aws_secret_access_key=secrets.SECRET_KEY
)

ses_response = ses.send_email(
    Source=email_origin,
    Destination={
        'ToAddresses': email_destination,
        'CcAddresses': [],
        'BccAddresses': []
    },
    Message={
        'Subject': {
            'Data': 'Backup %s ok %s UTC' % (db_name, date.strftime('%Y-%m-%dT%H:%M:%S'),),
            'Charset': 'utf-8'
        },
        'Body': {
            'Text': {
                'Data': 'Backup for database %s ok at %s UTC - S3 Key: %s' %
                        (db_name, date.strftime('%Y-%m-%dT%H:%M:%S'), s3_key),
                'Charset': 'utf-8'
            }
        }
    }
)

# Remove the files in the local drive
os.remove('%s/%s' % (cwd, dump_name))
os.remove('%s/%s' % (cwd, dump_name_gz))

sys.exit(0)
