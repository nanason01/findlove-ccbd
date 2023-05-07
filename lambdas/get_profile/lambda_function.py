import json

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
#     "statusCode": 200,
#     "user": {
#         "field": "field_value",
#         ... (other fields) ...
#     }
# }
# Expected response format if user doesn't exist:
#
# {
#     "statusCode": 404
# }


@CORS
def lambda_handler(event, _):
    user_id = event['pathParameters']['id']

    if not users.user_exists(user_id):
        return {'statusCode': 404}

    return {
        'statusCode': 200,
        'user': users.get_user(user_id)
    }
