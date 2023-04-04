import boto3
from botocore.exceptions import ClientError


table_name = 'decisions'
dynamodb = boto3.client('dynamodb')

# Expected event format:
#
# {
#     "user_id": "string",
#     "candidate_id": "string",
#     "liked": "bool"
# }
#
# Expected response format:
#
# {
#     "statusCode": 200
#     "isMatch": "bool"
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


def decision_exists(user_id: str, candidate_id: str) -> bool:
    try:
        table_name = 'decisions'
        response = dynamodb.get_item(
            TableName=table_name,
            Key={
                'user_id': {'S': user_id},
                'candidate_id': {'S': candidate_id}
            }
        )
        print('decision exists resp:', response)
        return 'Item' in response
    except Exception as e:
        print('decision exists error:', e)
        return False


def add_match(user_1, user_2):
    table_name = 'users'

    # Get the current matches list for user 1
    response = dynamodb.get_item(
        TableName=table_name,
        Key={'id': {'S': user_1}},
        ProjectionExpression='matches'
    )
    matches = response['Item']['matches']['SS'] if 'matches' in response['Item'] else []

    # Add user 2 to the matches list for user 1
    print('adding matches for', user_1, 'with current matches', matches)
    matches.append(user_2)

    # Update the matches list for user 1
    response = dynamodb.update_item(
        TableName=table_name,
        Key={'id': {'S': user_1}},
        UpdateExpression='SET matches = :matches',
        ExpressionAttributeValues={':matches': {'SS': matches}}
    )

    # Get the current matches list for user 2
    response = dynamodb.get_item(
        TableName=table_name,
        Key={'id': {'S': user_2}},
        ProjectionExpression='matches'
    )
    matches = response['Item']['matches']['SS'] if 'matches' in response['Item'] else []

    # Add user 1 to the matches list for user 2
    matches.append(user_1)

    # Update the matches list for user 2
    response = dynamodb.update_item(
        TableName=table_name,
        Key={'id': {'S': user_2}},
        UpdateExpression='SET matches = :matches',
        ExpressionAttributeValues={':matches': {'SS': matches}}
    )


def lambda_handler(event, _):
    # TODO should we validate the URL

    print(event)

    if not user_exists(event['user_id']):
        print(f"User {event['user_id']} does not exist")
        return {'statusCode': 404}

    if not user_exists(event['candidate_id']):
        print(f"User {event['candidate_id']} does not exist")
        return {'statusCode': 404}

    # Put this decision

    item = {
        'user_id': {'S': event['user_id']},
        'candidate_id': {'S': event['candidate_id']},
        'liked': {'BOOL': event['liked']}
    }

    is_duplicate = decision_exists(event['user_id'], event['candidate_id'])
    if is_duplicate:
        print('Decision already made')
    else:
        print('Decision not yet made')

    try:
        response = dynamodb.put_item(
            TableName=table_name,
            Item=item
        )
        print(response)
    except ClientError as e:
        print(e)
        return {'statusCode': 500}

    # Check for a counter decision if this is a liked
    if not event['liked']:
        return {
            'statusCode': 200,
            'isMatch': False
        }

    response = dynamodb.query(
        TableName=table_name,
        KeyConditionExpression='#user_id = :user_id and #candidate_id = :candidate_id',
        ExpressionAttributeNames={
            '#user_id': 'user_id',
            '#candidate_id': 'candidate_id'
        },
        ExpressionAttributeValues={
            ':user_id': {'S': event['candidate_id']},
            ':candidate_id': {'S': event['user_id']}
        }
    )
    print(response)

    isMatch = response['Count'] > 0 and response['Items'][0]['liked']['BOOL']

    if isMatch and not is_duplicate:
        add_match(event['user_id'], event['candidate_id'])

    return {
        'statusCode': 200,
        'isMatch': isMatch
    }
