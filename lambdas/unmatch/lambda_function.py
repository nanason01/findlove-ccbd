from botocore.exceptions import ClientError

from common import users, decisions
from common.CORS import CORS

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


@CORS
def lambda_handler(event, _):
    print(event)

    user_id = event['pathParameters']['id']
    match_id = event['queryStringParameters']['unmatchedId']

    if not users.user_exists(user_id):
        return {'statusCode': 404}

    # not currently matched case
    # TODO: should this return 200?
    # TODO: if so, should we handle match_id isn't a valid user case?
    matches = users.get_matches(user_id)
    if match_id not in matches:
        return {'statusCode': 404}

    users.remove_match(user_id, match_id)
    decisions.put_decision(user_id, match_id, False)

    return {'statusCode': 200}
