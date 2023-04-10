import boto3
from botocore.exceptions import ClientError

table_name = 'decisions'
dynamodb = boto3.client('dynamodb')

# Expected event format:
#
# {
#     "user_id": "string",
#     TODO: add more fields, integrate them to query spotify if not coming from frontend
# }
#
# Expected response format if successful:
#
# {
#     "statusCode": 200
# }
# Expected response format if user already exists:
#
# {
#     "statusCode": 409
# }


def user_exists(user_id: str) -> bool:
    try:
        table_name = 'users'
        response = dynamodb.get_item(
            TableName=table_name,
            Key={'id': {'S': user_id}},
            ProjectionExpression='id'
        )
        print('user exists resp:', response)
        return 'Item' in response
    except Exception as e:
        print('user exists error:', e)
        return False


def lambda_handler(event, _):
    print(event)

    if user_exists(event['user_id']):
        return {'statusCode': 409}

    table_name = 'users'
    item = {
        'user_id': {'S': event['user_id']}
    }

    try:
        response = dynamodb.put_item(
            TableName=table_name,
            Item=item
        )
        print(response)
        return {'statusCode': 200}
    except ClientError as e:
        print(e)
        return {'statusCode': 500}
