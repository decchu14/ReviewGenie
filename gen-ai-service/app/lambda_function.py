import json
from fetch_diffapi import get_response
from db_handler import  saveReponse

def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])

        project_id = body['project_id']
        mr_iid = body['mr_iid']
        action = "open"

        print(f"Received Project ID: {project_id}, MR ID: {mr_iid}")
        response={}
        # Call your second service logic
        if action in ["open", "reopen", "update"]:
            answer=get_response(project_id, mr_iid)
            response=saveReponse(answer,project_id,mr_iid)


    return {
        'statusCode': 200,
        'body': response
    }
