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
    content_object = s3.Object(S3_BUCKET, CONFIG_FILE)
    content_object.put(
        Body=(bytes(json.dumps(event, indent=4).encode('UTF-8')))
    )

    return {"status": "Config updated"}
