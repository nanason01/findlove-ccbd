import boto3

table_name = 'users'
dynamodb = boto3.client('dynamodb')

# Expected event format:
#
# {
#     "user_id": "string"
# }
#
# Expected response format if successful:
#
# {
#     "statusCode": 200
#     "matches": ["match_id1", "match_id2", ...] (may be empty)
# }
# Expected response format if user doesn't exist:
#
# {
#     "statusCode": 404
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
    user_id = event['user_id']

    if not user_exists(user_id):
        return {'statusCode': 404}

    response = dynamodb.get_item(
        TableName=table_name,
        Key={'id': {'S': user_id}},
        ProjectionExpression='matches'
    )
    matches = response['Item']['matches']['SS'] if 'matches' in response['Item'] else []

    return {
        'statusCode': 200,
        "matches": matches
    }
