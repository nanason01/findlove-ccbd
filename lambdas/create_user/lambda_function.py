from botocore.exceptions import ClientError
import json

from common import users
from common.CORS import CORS

# Expected event format:
#
# {
#     "user_id": "string",
#     "field": "field_value",
#     ... (other fields) ...
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


@CORS
def lambda_handler(event, _):
    user_id = event['pathParameters']['id']
    fields = json.loads(event['body'])

    if users.user_exists(user_id):
        return {'statusCode': 409}

    users.create_user(user_id, **fields)
    return {'statusCode': 200}
