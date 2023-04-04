import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.client('dynamodb')

# Expected event format:
#
# {
#     "user_id": "string",
#     "match_id": "string"
# }
#
# Expected response format if successful, or match not in user's matches:
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
    match_id = event['match_id']

    if not user_exists(user_id):
        return {'statusCode': 404}

    remove_from_matches_list(user_id, match_id)
    remove_from_matches_list(match_id, user_id)

    # Put a rejection decision
    table_name = 'decisions'
    response = dynamodb.update_item(
        TableName=table_name,
        Key={'user_id': {'S': user_id}, 'candidate_id': {'S': match_id}},
        UpdateExpression='SET liked = :liked',
        ExpressionAttributeValues={':liked': {'BOOL': False}}
    )
    print('resp from put to decisions:', response)

    return {'statusCode': 200}
