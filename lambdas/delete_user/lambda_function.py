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

    if match_id not in matches:
        return

    # Remove the match ID from the matches list
    matches.remove(match_id)

    # Update the matches list for the user
    response = None
    if matches:
        response = dynamodb.update_item(
            TableName=table_name,
            Key={'id': {'S': user_id}},
            UpdateExpression='SET matches = :matches',
            ExpressionAttributeValues={':matches': {'SS': matches}}
        )
    else:
        response = dynamodb.update_item(
            TableName=table_name,
            Key={'id': {'S': user_id}},
            UpdateExpression='REMOVE matches'
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

    # This will leave references in the decisions table, these are tiny per user
    # and less expensive to just let TTL get them than a scan.

    # Delete the user
    table_name = 'users'
    response = dynamodb.delete_item(
        TableName=table_name,
        Key={'id': {'S': user_id}}
    )

    return {'statusCode': 200}
