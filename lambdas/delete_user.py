import boto3
from botocore.exceptions import ClientError

table_name = 'decisions'
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


def remove_from_matches_list(user_id, match_id):
    # Get the current matches list for the user
    table_name = 'users'
    response = dynamodb.get_item(
        TableName=table_name,
        Key={'id': {'S': user_id}},
        ProjectionExpression='matches'
    )
    matches = response['Item']['matches']['SS'] if 'matches' in response['Item'] else []

    # Remove the match ID from the matches list
    matches.remove(match_id)

    # Update the matches list for the user
    response = dynamodb.update_item(
        TableName=table_name,
        Key={'id': {'S': user_id}},
        UpdateExpression='SET matches = :matches',
        ExpressionAttributeValues={':matches': {'SS': matches}}
    )

    # Print the response
    print('removing match', match_id, 'from', user_id, 'table resp:', response)


def lambda_handler(event, _):
    print(event)
    user_id = event['user_id']

    if not user_exists(user_id):
        return {'statusCode': 404}

    # Get the current matches list for user
    table_name = 'users'
    response = dynamodb.get_item(
        TableName=table_name,
        Key={'id': {'S': user_id}},
        ProjectionExpression='matches'
    )
    matches = response['Item']['matches']['SS'] if 'matches' in response['Item'] else []

    # Remove user from every match list they're on
    print(f"Removing matches for {user_id}...")
    for match in matches:
        print(f"Removing {user_id} from {match}'s match list")
        remove_from_matches_list(match, user_id)

    # Remove any decisions referrencing user
    print('Updating decisions table...')
    table_name = 'decisions'
    delete_query = {
        'TableName': table_name,
        'KeyConditionExpression': '#user_id = :user_id OR #candidate_id = :candidate_id',
        'ExpressionAttributeNames': {
            '#user_id': 'user_id',
            '#candidate_id': 'candidate_id'
        },
        'ExpressionAttributeValues': {
            ':user_id': {'S': user_id},
            ':candidate_id': {'S': user_id}
        }
    }

    response = dynamodb.query(**delete_query)
    for item in response['Items']:
        dynamodb.delete_item(TableName=table_name, Key={
                             'user_id': item['user_id'], 'candidate_id': item['candidate_id']})

    # Delete the user
    table_name = 'users'
    response = dynamodb.delete_item(
        TableName=table_name,
        Key={'id': {'S': user_id}}
    )

    return {'statusCode': 200}
