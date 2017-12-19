Run with Python3  

Create a secrets.py file with the credentials and config values.  

```python
DATABASE_NAME = '<date-base-name>'

DATABASE_DUMP_NAME = '<data-base-dump-file.sql>'

BUCKET_NAME = '<s3-bucket-destination>'

ACCESS_KEY = '<aws-access-key>'

SECRET_KEY = '<aws-secret-key>'

EMAIL_ORIGIN = '<aws-ses-confirmed-email>'

EMAIL_DESTINATION = ['<list-of-destination-emails>']
```  

Install boto3: `pip install boto3`  

And run with command: `python3 pg_backup.py`  