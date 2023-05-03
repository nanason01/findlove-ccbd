from botocore.exceptions import ClientError

from common import users, decisions
from common.CORS import CORS
import json

from rank_candidates import get_best_candidate

SAMPLE_SIZE = 10        # cands per sample
GOOD_SAMPLE_SIZE = 5    # valid cands to stop sampling
NUM_RETRIES = 3         # resamples before giving up

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
#     "candidate_found": True,
#     "candidate_id": "string",
#     "reason": "string"
# }
#
# Response format if no eligible candidates:
#
# {
#     "statusCode": 200,
#     "candidate_found": False
# }
#
# Expected response format if user doesn't exist:
#
# {
#     "statusCode": 404
# }


@CORS
def lambda_handler(event, _):
    print(event)
    user_id = event['queryStringParameters']['id']

    if not users.user_exists(user_id):
        print("If user not exists stmt")
        return {'statusCode': 404}

    candidate_ids = []
    for _ in range(NUM_RETRIES):
        sample = users.sample_users(n=SAMPLE_SIZE)

        candidate_ids += [
            candidate_id for candidate_id in sample
            if candidate_id != user_id and
            not decisions.decision_exists(user_id, candidate_id)
        ]

        if len(candidate_ids) >= GOOD_SAMPLE_SIZE:
            break

    if not candidate_ids:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'candidate_found': False,
            })
        }

    candidate_id, reason = get_best_candidate(user_id, candidate_ids)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'candidate_found': True,
            'candidate_id': candidate_id,
            'reason': reason
        })
    }
