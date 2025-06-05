import json
import os
import urllib3
import boto3

http = urllib3.PoolManager()
sqs = boto3.client('sqs')

GITLAB_TOKEN = os.environ['GITLAB_TOKEN']
GITLAB_API_URL = "https://gitlab.com/api/v4"
SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        print("Webhook received from GitLab")

        project_id = body['project']['id']
        mr_iid = body['object_attributes']['iid']
        action = body['object_attributes']['action']

        if action not in ['open', 'update', 'reopen', 'close']:
            print("Action not supported, ignoring")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'ok'})
            }
            
        # Build message for SQS
        message = {
            "event_type": "merge_request",
            "project_id": project_id,
            "mr_iid": mr_iid,
            "action": action
        }

        # Send to SQS
        response = sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message)
        )

        print("Message sent to SQS:", response)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'ok'})
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'error', 'error': str(e)})
        }