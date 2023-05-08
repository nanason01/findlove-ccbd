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
    user_ids_str = event['queryStringParameters']['ids']
    user_ids = user_ids_str.split(',')

    print("In get_profiles")
    # if not users.user_exists(user_id):
    #     print("In user doesn't exit call")
    #     return {'statusCode': 404}
    #
    print("Get user called")

    user_objs = users.get_users_by_ids(user_ids)
    print(user_objs)
    return {
        'statusCode': 200,
        'body': json.dumps({
            'users': user_objs
        })
    }
