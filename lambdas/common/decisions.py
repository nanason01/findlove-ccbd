import boto3
from boto3.dynamodb.conditions import Key

from typing import List, Dict
from datetime import datetime
import time
import enum

table_name = 'decisions'
dynamodb = boto3.client('dynamodb')
decisions = dynamodb.Table(table_name)


class DecisionStatus(enum.Enum):
    NoDecision = 1
    Liked = 2
    Disliked = 3


def decision_exists(user_id: str, candidate_id: str) -> bool:
    """Return whether a decision has been made for this pair

    Args:
        user_id (str): user_id of user making decision
        candidate_id (str): user_id of object of decision

    Returns:
        bool: true iff this decision already exists

    Raises:
        ClientError: dynamoDB failure
    """
    response = decisions.query(
        KeyConditionExpression=(Key('user_id').eq(
            user_id) & Key('candidate_id').eq(candidate_id))
    )
    return len(response['Items']) > 0


def put_decision(user_id: str, candidate_id: str, liked: bool):
    """Add a decision, return whether successfully put

    Note: does not check whether decision exists

    Args:
        user_id (str): user_id of user making decision
        candidate_id (str): user_id of object of decision
        liked (bool): true iff user_id liked candidate_id

    Raises:
        ClientError: dynamoDB failure
    """
    item = {
        'user_id': user_id,
        'candidate_id': candidate_id,
        'liked': liked,
    }

    decisions.put_item(Item=item)


def decision_status(user_id: str, candidate_id: str) -> DecisionStatus:
    """Return the status of this decision

    Args:
        user_id (str): user_id of user making decision
        candidate_id (str): user_id of object of decision

    Raises:
        ClientError: dynamoDB failure
    """
    response = decisions.query(
        KeyConditionExpression=(Key('user_id').eq(
            user_id) & Key('candidate_id').eq(candidate_id))
    )
    if len(response['Items']) == 0:
        return DecisionStatus.NoDecision
        # TODO: check this response parsing
    elif response['Items'][0]['liked']:
        return DecisionStatus.Liked
    else:
        return DecisionStatus.Disliked
