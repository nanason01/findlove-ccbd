import json

from common import users
from common.CORS import CORS

# Expected event format:
#
# {
#     "user_id": "string",
#     "field": "field_value",
#     ... (other fields to change) ...
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


@CORS
def lambda_handler(event, _):
    print(event)
    user_id = event['pathParameters']['id']
    changed_fields = json.loads(event['body'])

    if not users.user_exists(user_id):
        return {'statusCode': 404}

    users.update_user(user_id, **changed_fields)
    return {'statusCode': 200}
