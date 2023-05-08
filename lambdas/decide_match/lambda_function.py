import json

import boto3
from botocore.exceptions import ClientError
import random

from common import users, decisions
from common.CORS import CORS

ses = boto3.client('ses')
SOURCE_EMAIL = "findlove6998@gmail.com"

# Expected event format:
#
# {
#     "user_id": "string",
#     "candidate_id": "string",
#     "liked": "bool"
# }
#
# Expected response format:
#
# {
#     "statusCode": 200
#     "isMatch": "bool"
# }


def notify_match(candidate_id, user_id):
    candidate = users.get_user(candidate_id)
    user = users.get_user(user_id)

    subject = random.choice([
        "You're about to catch a groove",
        "The beat's picking up",
        "It's about to get more funky",
    ])

    body = f"You just matched with {user['first_name']}, play it cool by messaging them right away!"

    try:
        ses.send_email(
            Source=SOURCE_EMAIL,
            Destination={
                'ToAddresses': [candidate['email']],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': 'utf-8',
                        'Data': body,
                    },
                },
                'Subject': {
                    'Charset': 'utf-8',
                    'Data': subject,
                },
            },
        )
    except Exception:
        print('unable to notify match counterparty')


@CORS
def lambda_handler(event, _):
    # TODO: fixup these
    user_id = event['queryStringParameters']['id']
    candidate_id = event['queryStringParameters']['candidateId']
    liked = event['queryStringParameters']['isMatch']

    if not users.user_exists(user_id):
        print(f"User {user_id} does not exist")
        return {'statusCode': 404}

    if not users.user_exists(candidate_id):
        print(f"User {candidate_id} does not exist")
        return {'statusCode': 404}

    curr_status = decisions.decision_status(user_id, candidate_id)
    counter_status = decisions.decision_status(candidate_id, user_id)

    # decision already recorded, duplicate request case
    if curr_status != decisions.DecisionStatus.NoDecision:
        if liked != (curr_status == decisions.DecisionStatus.Liked):
            # TODO: is there a better way to handle this?
            raise Exception(
                "decide match doesn't let you change your mind")

        is_match = liked and counter_status == decisions.DecisionStatus.Liked
        return {'statusCode': 200, 'body': json.dumps({'isMatch': is_match})}

    decisions.put_decision(user_id, candidate_id, liked)

    is_match = liked and counter_status == decisions.DecisionStatus.Liked

    if is_match:
        users.add_match(user_id, candidate_id)
        notify_match(candidate_id, user_id)

    return {'statusCode': 200, 'body': json.dumps({'isMatch': is_match})}
