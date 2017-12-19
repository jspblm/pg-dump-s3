""" Database backup """

import subprocess
import datetime
import os
import sys

import boto3
import secrets


dump_name = secrets.DATABASE_DUMP_NAME
db_name = secrets.DATABASE_NAME
email_origin = secrets.EMAIL_ORIGIN
email_destination = secrets.EMAIL_DESTINATION

cwd = os.getcwd()

dump = subprocess.run(['pg_dump', '-d', db_name, '-f', dump_name],
                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

if dump.stdout:
    print('[ERROR]', dump.stdout)
    sys.exit(1)

s3 = boto3.client(
    's3',
    aws_access_key_id=secrets.ACCESS_KEY,
    aws_secret_access_key=secrets.SECRET_KEY
)

date = datetime.datetime.utcnow()

s3.upload_file(dump_name, secrets.BUCKET_NAME, '%s-%s-UTC.sql' % (db_name, date.strftime('%Y-%m-%dT%H')))

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
                'Data': 'Backup for database %s ok at %s UTC' % (db_name, date.strftime('%Y-%m-%dT%H:%M:%S'),),
                'Charset': 'utf-8'
            }
        }
    }
)


os.remove('%s/%s' % (cwd, dump_name))

sys.exit(0)

