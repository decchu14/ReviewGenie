import json
import requests
import urllib.parse
import boto3
import os

GITLAB_TOKEN = os.environ['GITLAB_TOKEN']
GITLAB_API_URL = os.environ['GITLAB_API_URL']

dynamodb = boto3.client('dynamodb')
DYNAMODB_TABLE = 'MRAnalysisResults'

def post_gitlab_comment(project_id, mr_iid, analysis):
    # URL encode project_id if it contains slashes or special chars
    project_id_encoded = urllib.parse.quote_plus(str(project_id))

    url_notes = f"{GITLAB_API_URL}/projects/{project_id_encoded}/merge_requests/{mr_iid}/notes"
    headers = {'PRIVATE-TOKEN': GITLAB_TOKEN}
    data = {'body': analysis}

    post_resp = requests.post(url_notes, headers=headers, data=data)
    if post_resp.status_code == 201:
        print(f"Posted new comment on MR {mr_iid}")
        return True
    else:
        print(f"Failed to post comment: {post_resp.status_code} {post_resp.text}")
        return False

def delete_dynamo_record(project_id, mr_iid):
    try:
        response = dynamodb.delete_item(
            TableName=DYNAMODB_TABLE,
            Key={
                'mr_iid': {'S': mr_iid},
                'project_id': {'S': project_id}
            }
        )
        print(f"Deleted DynamoDB record for MR {mr_iid}, Project {project_id}")
        return True
    except Exception as e:
        print(f"Failed to delete DynamoDB record: {e}")
        return False

def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] in ['INSERT', 'MODIFY']:  # handle new or updated items
            new_image = record['dynamodb']['NewImage']
            print(f"New image: {new_image}")
            # Extract values from DynamoDB's special format
            mr_iid = new_image['mr_iid']['S']
            project_id = new_image['project_id']['S']
            analysis = new_image['analysis']['S']

            print(f"Processing MR {mr_iid} for project {project_id}")
            success = post_gitlab_comment(project_id, mr_iid, analysis)

            # if post success, delete the item from DynamoDB
            if success:
                delete_dynamo_record(project_id, mr_iid)
    return {
        'statusCode': 200,
        'body': json.dumps('Processing done.')
    }