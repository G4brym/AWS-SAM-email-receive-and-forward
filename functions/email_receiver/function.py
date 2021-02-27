import email
import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
ses = boto3.client('ses')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if "SENTRY_DSN" in os.environ and os.environ["SENTRY_DSN"] != "disabled":
    import sentry_sdk
    from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

    logger.info(
        "SUCCESS: Sentry configured with DSN: {}".format(os.environ["SENTRY_DSN"])
    )
    sentry_sdk.init(dsn=os.environ["SENTRY_DSN"], integrations=[AwsLambdaIntegration()])

S3_BUCKET = os.environ['S3_BUCKET']
CONFIG_FILE = os.environ.get('CONFIG_FILE', 'configs.json')


def get_configs():
    object_s3 = s3.get_object(Bucket=S3_BUCKET, Key=CONFIG_FILE)
    file = object_s3['Body'].read().decode('utf-8')

    return json.loads(file)


CONFIG = get_configs()


def get_email(message_id):
    unprocessed_location = "{}/{}".format(CONFIG["unprocessed_path"], message_id)
    logger.info("location: {}".format(unprocessed_location))

    o = s3.get_object(Bucket=S3_BUCKET, Key=unprocessed_location)
    raw_mail = o['Body'].read()
    msg = email.message_from_bytes(raw_mail)

    original_from = msg['From']

    del msg['DKIM-Signature']
    del msg['Sender']
    del msg['Return-Path']
    del msg['Reply-To']
    del msg['From']

    logger.info("from: {}".format(original_from))

    name = None
    if "<" in original_from and ">" in original_from:
        name = original_from.split("<")[0].strip()

    logger.info("name: {}".format(name))

    if name:
        msg['From'] = "{} <{}>".format(name, CONFIG["from_email"])
    else:
        msg['From'] = CONFIG["from_email"]

    logger.info("from: {}".format(msg['From']))

    msg['Reply-To'] = original_from
    msg['Return-Path'] = msg['From']

    # logger.info("m: {}".format(msg))

    return msg.as_string()


def send_email(email, recipients):
    for recipient in recipients:
        logger.info("recipient: {}".format(recipient))
        forwards = CONFIG["mapping"].get(recipient, [])
        if not forwards:
            _domain = "@{}".format(recipient.split("@")[1])
            forwards = CONFIG["mapping"].get(_domain, [])

        if not forwards:
            logger.warning('Recipent <{}> is not found in forwarding map, using fallback email {}.'.format(recipient, CONFIG["receipt_fallback"]))
            forwards = [CONFIG["receipt_fallback"], ]

        for address in forwards:
            logger.info("addr: {}".format(address))

            try:
                o = ses.send_raw_email(Destinations=[address], RawMessage=dict(Data=email))
                logger.info('Forwarded email for <{}> to <{}>. SendRawEmail response={}'.format(recipient, address, json.dumps(o)))
            except ClientError as e:
                logger.error('Client error while forwarding email for <{}> to <{}>: {}'.format(recipient, address, e))
                raise e


def move_email_to_processed(message_id, recipients):
    domain = recipients[0].split("@")[1]

    unprocessed_location = "{}/{}".format(CONFIG["unprocessed_path"], message_id)
    target_location = "domains/{}/{}".format(domain, message_id)

    s3.copy({'Bucket': S3_BUCKET, 'Key': unprocessed_location}, Bucket=S3_BUCKET, Key=target_location)
    s3.delete_object(Bucket=S3_BUCKET, Key=unprocessed_location)


def handler(event, context):
    record = event['Records'][0]
    assert record['eventSource'] == 'aws:ses'

    message_id = record['ses']['mail']['messageId']
    recipients = record['ses']['receipt']['recipients']

    email = get_email(message_id)

    send_email(email, recipients)

    move_email_to_processed(message_id, recipients)

    return True
