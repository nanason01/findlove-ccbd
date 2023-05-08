import simplejson as json

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
    print("In get_profile")
    if not users.user_exists(user_id):
        print("In user doesn't exit call")
        return {'statusCode': 404}
    
    print("Get user called")
    user = users.get_user(user_id)
    print(user)
    return {
        'statusCode': 200,
        'body': json.dumps({
            'user': user
        })
    }
