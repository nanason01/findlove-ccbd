from botocore.exceptions import ClientError

from common import users, decisions
from common.CORS import CORS

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


@CORS
def lambda_handler(event, _):
    # TODO: fixup these
    user_id = event['user_id']
    candidate_id = event['candidate_id']
    liked = event['liked']

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
        return {'statusCode': 200, 'isMatch': is_match}

    decisions.put_decision(user_id, candidate_id, liked)

    is_match = liked and counter_status == decisions.DecisionStatus.Liked

    if is_match:
        users.add_match(user_id, candidate_id)

    return {'statusCode': 200, 'isMatch': is_match}
