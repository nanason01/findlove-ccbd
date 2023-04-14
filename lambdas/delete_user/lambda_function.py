from botocore.exceptions import ClientError

import common.users
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
# }
# Expected response format if user doesn't exist:
#
# {
#     "statusCode": 404
# }


@CORS
def lambda_handler(event, _):
    user_id = event['user_id']

    try:
        if not users.user_exists(user_id):
            return {'statusCode': 404}

        users.delete_user(user_id)
        return {'statusCode': 200}

    except ClientError as e:
        print(e)
        return {'statusCode': 500}
