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
#     "statusCode": 200,
#     "candidate_found": True
#     "candidate_id": "string"
# }
#
# Response format if no eligible candidates:
#
# {
#     "statusCode": 200,
#     "candidate_found": False
# }
#
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

    response = dynamodb.query(
        TableName=table_name,
        KeyConditionExpression='user_id = :user_id',
        ExpressionAttributeValues={':user_id': {'S': user_id}},
        ProjectionExpression='candidate_id'
    )

    # Extract the list of candidate_ids from the response
    already_decided = [item['candidate_id']['S'] for item in response['Items']]

    # Query the table for a user not in the exclude_ids set
    response = dynamodb.query(
        TableName=table_name,
        KeyConditionExpression='id > :id',
        ExpressionAttributeValues={':id': {'S': '0'}},
        FilterExpression='NOT id IN (:exclude_ids)',
        ExpressionAttributeValues={':exclude_ids': {'SS': already_decided}},
        Limit=1,
        ScanIndexForward=True
    )

    candidate = response['Item'][0]['id']['S'] if 'Item' in response and len(
        response['Item']) > 0 else None

    if candidate:
        return {
            'statusCode': 200,
            'candidate_found': True,
            'candidate': candidate
        }
    else:
        return {
            'statusCode': 200,
            'candidate_found': False
        }
