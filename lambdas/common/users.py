import boto3
from boto3.dynamodb.conditions import Key
import random

from typing import List, Dict
from datetime import datetime
import time


table_name = 'users'
dynamodb = boto3.client('dynamodb')
users = dynamodb.Table(table_name)


def user_exists(user_id: str) -> bool:
    """Returns whether user exists

    Args:
        user_id (str): user_id to check for

    Returns:
        bool: True iff user_id in users

    Raises:
        ClientError: dynamoDB failure
    """
    response = users.query(
        KeyConditionExpression=Key('user_id').eq(user_id)
    )

    return len(response['Items']) > 0


def get_user(user_id: str):
    """_summary_

    Args:
        user_id (str): user id to get

    Raises:
        Exception: user does not exist
        ClientError: dynamoDB failure

    Returns:
        user object
    """
    response = users.query(
        KeyConditionExpression=Key('user_id').eq(user_id)
    )

    if len(response['Items']) == 0:
        raise Exception(f'Get user error: {user_id} does not exist')

    return response['Items'][0]


# TODO: add location, spotify data to create, update
def create_user(
    user_id: str,
    first_name: str,
    last_name: str,
    email: str,
    dob: str,
    phone: str,
    gender: str,
    orientation: List[str]
):
    """Update a user item with these characteristics

    Requires user_id or dict (with user id)

    Args:
        user_id (str)
        first_name (str)
        last_name (str)
        email (str)
        dob (str)
        phone (str)
        gender (str)
        orientation (List[str])

    Raises:
        ClientError: dynamoDB failure
    """
    unix_dob = int(time.mktime(datetime.strptime(dob, '%m/%d/%Y')))

    item = {
        'user_id': user_id,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'dob': unix_dob,
        'phone': phone,
        'gender': gender,
        'orientation': orientation
    }

    users.put_item(Item=item)


valid_fields = {
    'first_name',
    'last_name',
    'email',
    'dob',
    'phone',
    'gender',
    'orientation',
}


def update_user(user_id: str, **fields):
    """Update fields given for user_id

    See valid_fields for valid kwarg keys

    Args:
        user_id (str): user_id to update on

    Raises:
        ClientError: dynamoDB failure
        Exception: raises if invalid field passed
    """
    if any(field not in valid_fields for field in fields):
        raise Exception('Invalid field in: ' + str(fields))

    update_expression = ', '.join([
        f'SET #{field} = :new_{field}'
        for field in fields
    ])

    expression_attribute_names = {
        f'#{field}': field for field in fields
    }

    expression_attribute_values = {
        f':new_{field}': new_value
        for field, new_value in fields.items()
    }

    users.update_item(
        Key={'user_id': user_id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values
    )


def delete_user(user_id: str):
    """Deletes a user from the users table

    Note: does NOT check whether user actually existed

    Args:
        user_id (str): user id to delete

    Raises:
        ClientError: dynamoDB failure
    """
    matches = get_matches(user_id)

    for match in matches:
        remove_match_one_side(match, user_id)

    users.delete_item(
        Key={'user_id': user_id}
    )


def get_matches(user_id: str) -> List[str]:
    """Get matches for user

    Returns [] if error encountered

    Args:
        user_id (str): user id to get matches for

    Returns:
        List[str]: list of ids that user is matched to

    Raises:
        ClientError: dynamoDB failure
    """
    response = users.get_item(
        Key={'id': {'S': user_id}},
        ProjectionExpression='matches'
    )
    return response['Item']['matches']['SS'] if 'matches' in response['Item'] else []


def add_match(user_1: str, user_2: str):
    """Add match between user_1 and user_2

    Requires: user_1 and user_2 aren't already matched

    Args:
        user_1 (str): user to match
        user_2 (str): user to match

    Raises:
        ClientError: dynamoDB failure
    """
    # Get current matches for user 1 and user 2
    user_1_matches = get_matches(user_1)
    user_2_matches = get_matches(user_2)

    # Update matches tables
    user_1_matches.append(user_2)
    user_2_matches.append(user_1)

    # Put updated tables back in users
    users.update_item(
        Key={'id': user_1},
        UpdateExpression='SET matches = :matches',
        ExpressionAttributeValues={':matches': {'SS': user_1_matches}}
    )
    users.update_item(
        Key={'id': user_2},
        UpdateExpression='SET matches = :matches',
        ExpressionAttributeValues={':matches': {'SS': user_2_matches}}
    )


def remove_match_one_side(user_id: str, match_id: str):
    """Remove match_id from user_id's matches list

    Args:
        user_id (str): user id to edit matches for
        match_id (str): user id to remove

    Raises:
        Exception: users not currently matched
        ClientError: dynamoDB failure
    """
    matches = get_matches(user_id)

    if match_id not in matches:
        raise Exception(
            f"remove match error: {user_id} not currently matched with {match_id}")

    matches.remove(match_id)

    if matches:
        users.update_item(
            Key={'id': user_id},
            UpdateExpression='SET matches = :matches',
            ExpressionAttributeValues={':matches': {'SS': matches}}
        )
    else:
        users.update_item(
            Key={'id': user_id},
            UpdateExpression='REMOVE matches'
        )


def remove_match(user_1: str, user_2: str):
    """Remove match between user 1 and user 2 in matches table

    Args:
        user_1 (str): user to unmatch
        user_2 (str): user to unmatch

    Raises:
        Exception: users not currently matched
        ClientError: dynamoDB failure
    """
    remove_match_one_side(user_1, user_2)
    remove_match_one_side(user_2, user_1)


def sample_users(n: int = 10) -> List[str]:
    """Return a random sample of n users

    Args:
        n (int, optional): number of users in sample. Defaults to 10.

    Returns:
        List[str]: user ids of users found
    """
    # Get the total number of items in the table
    total_items = users.item_count

    # Generate 10 random indices to select items from the table
    random_indices = random.sample(range(total_items), 10)

    # Retrieve the user IDs for the randomly selected items
    user_ids = []
    for index in random_indices:
        response = users.scan(
            ProjectionExpression='user_id',
            Limit=1,
            ExclusiveStartKey={'id': index + 1}
        )
        user_ids.append(response['Items'][0]['user_id'])

    return user_ids