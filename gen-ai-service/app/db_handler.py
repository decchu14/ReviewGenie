import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('MRAnalysisResults')


def saveReponse(answer,project_id,mr_id):

    print(f"Received Project ID: {project_id}, MR ID: {mr_id}")

    result = {
        'project_id': str(project_id),
        'mr_iid':str(mr_id),
        'analysis': str(answer)
    }

    try:
        table.put_item(Item=result)
        print(f"Stored to DynamoDB: {result}")
    except ClientError as e:
        print(f"Error storing to DynamoDB: {e.response['Error']['Message']}")


    return {
        'statusCode': 200,
        'body': result
    }