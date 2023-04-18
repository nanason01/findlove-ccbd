from botocore.exceptions import ClientError

from common import users
from common.CORS import CORS

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


@CORS
def lambda_handler(event, _):
    print(event)
    user_id = event['user_id']

    if not users.user_exists(user_id):
        return {'statusCode': 404}

    return {
        'statusCode': 200,
        'matches': users.get_matches(user_id),
    }
