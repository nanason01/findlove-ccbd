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


PREFERENCE_TO_GENDER = {
    'straight': {
        'M': {'F'},
        'F': {'M'},
        'O': {'M', 'F', 'O'},
    },
    'gay': {
        'M': {'M'},
        'F': {'F'},
        'O': {'M', 'O'},
    },
    'lesbian': {
        'M': {'F'},
        'F': {'F'},
        'O': {'F', 'O'},
    },
    'bisexual': {
        'M': {'M', 'F'},
        'F': {'M', 'F'},
        'O': {'M', 'F', 'O'},
    },
    'asexual': {
        'M': {'M', 'F', 'O'},
        'F': {'M', 'F', 'O'},
        'O': {'M', 'F', 'O'},
    },
    'demisexual': {
        'M': {'F'},
        'F': {'M'},
        'O': {'M', 'F', 'O'},
    },
    'pansexual': {
        'M': {'M', 'F', 'O'},
        'F': {'M', 'F', 'O'},
        'O': {'M', 'F', 'O'},
    },
    'queer': {
        'M': {'M', 'O'},
        'F': {'F', 'O'},
        'O': {'M', 'F', 'O'},
    },
}


@CORS
def lambda_handler(event, _):
    print(event)
    user_id = event['queryStringParameters']['id']

    if not users.user_exists(user_id):
        print("If user not exists stmt")
        return {'statusCode': 404}

    user = users.get_user(user_id)
    user_gender = user['gender']
    user_preferences = user['preference']

    gender_filter = {
        PREFERENCE_TO_GENDER[pref][user_gender]
        for user_pref in user_preferences for pref in user_pref
    }

    candidate_ids = []
    for _ in range(NUM_RETRIES):
        sample = users.sample_users(n=SAMPLE_SIZE)

        candidate_ids += [
            candidate['id'] for candidate in sample
            if candidate['id'] != user_id and
            not decisions.decision_exists(user_id, candidate['id']) and
            candidate['gender'] in gender_filter
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
