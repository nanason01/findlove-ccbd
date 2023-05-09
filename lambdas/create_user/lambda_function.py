from botocore.exceptions import ClientError
import boto3
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
# Expected response format if not enough tracks:
#
# {
#     "statusCode": 400
# }


ses = boto3.client('ses')


@CORS
def lambda_handler(event, _):
    user_id = event['pathParameters']['id']
    fields = json.loads(event['body'])

    if users.user_exists(user_id):
        return {'statusCode': 409}

    # check whether there are too few songs
    if len(fields.get('top_tracks', [])) < 50 or len(fields.get('top_artists', [])) < 50:
        return {'statusCode': 400}

    try:
        ses.verify_email_identity(EmailAddress=fields['email'])
    except Exception as e:
        print('failed to send verify email:', e)

    users.create_user(user_id, **fields)
    return {'statusCode': 200}
