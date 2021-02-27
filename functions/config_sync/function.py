import json
import logging
import os

import boto3

s3 = boto3.resource('s3')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

S3_BUCKET = os.environ['S3_BUCKET']
CONFIG_FILE = os.environ.get('CONFIG_FILE', 'configs.json')


def handler(event, context):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configs.json')) as fp:
        data = json.load(fp)

    content_object = s3.Object(S3_BUCKET, CONFIG_FILE)
    content_object.put(
        Body=(bytes(json.dumps(data).encode('UTF-8')))
    )

    return True
