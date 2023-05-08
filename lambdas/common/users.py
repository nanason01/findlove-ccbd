import boto3
from boto3.dynamodb.conditions import Key
import random

from typing import List, Dict
from datetime import datetime
import time


table_name = 'users'
dynamodb = boto3.resource('dynamodb')
users = dynamodb.Table(table_name)


valid_fields = {
    'first_name',
    'last_name',
    'email',
    'dob',
    'phone',
    'gender',
    'orientation',
    'top_artists',
    'top_tracks',
    'image_url'
}


def user_exists(id: str) -> bool:
    """Returns whether user exists

    Args:
        id (str): id to check for

    Returns:
        bool: True iff id in users

    Raises:
        ClientError: dynamoDB failure
    """
    response = users.query(
        KeyConditionExpression=Key('id').eq(id),
        ProjectionExpression='id'
    )

    return len(response['Items']) > 0


def get_user(id: str):
    """_summary_

    Args:
        id (str): user id to get

    Raises:
        Exception: user does not exist
        ClientError: dynamoDB failure

    Returns:
        user object
    """
    response = users.query(
        KeyConditionExpression=Key('id').eq(id)
    )

    if len(response['Items']) == 0:
        raise Exception(f'Get user error: {id} does not exist')

    return response['Items'][0]


def get_all_users():
    """_summary_

    Args:


    Raises:
        Exception: No users
        ClientError: dynamoDB failure

    Returns:
        all user objects
    """
    response = users.scan()

    if len(response['Items']) == 0:
        raise Exception(f'No users')

    return response['Items']


def get_users_by_ids(candidate_ids: str):
    """_summary_

    Args:


    Raises:
        Exception: No users
        ClientError: dynamoDB failure

    Returns:
        all user objects
    """
    # user_ids = ['id1', 'id2', 'id3']
    candidate_ids = candidate_ids.split(',')
    # candidate_ids = candidate_ids.strip('][').split(', ')
    print(candidate_ids)
    keys = [{'id': user_id} for user_id in candidate_ids]
    print(keys)
    params = {
        'RequestItems': {
            'users': {
                'Keys': keys
            }
        }
    }
    response = dynamodb.batch_get_item(**params)
    # response = users.scan()
    print(response)

    if len(response['Responses']['users']) == 0:
        raise Exception(f'No users')

    return response['Responses']['users']


def create_user(
    id: str,
    first_name: str,
    last_name: str,
    email: str,
    dob: str,
    phone: str,
    gender: str,
    orientation: List[str],
    top_artists,
    top_tracks,
    image_url: str
):
    """Update a user item with these characteristics

    Requires id or dict (with user id)

    Args:
        id (str)
        first_name (str)
        last_name (str)
        email (str)
        dob (str)
        phone (str)
        gender (str)
        orientation (List[str])
        top_artists
        top_tracks
        image_url (str)

    Raises:
        ClientError: dynamoDB failure
    """
    unix_dob = int(time.mktime(datetime.strptime(dob, '%m/%d/%Y').timetuple()))

    item = {
        'id': id,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'dob': unix_dob,
        'phone': phone,
        'gender': gender,
        'orientation': orientation,
        'top_artists': top_artists,
        'top_tracks': top_tracks,
        'image_url': image_url
    }

    users.put_item(Item=item)


def update_user(id: str, **fields):
    """Update fields given for id

    See valid_fields for valid kwarg keys

    Args:
        id (str): id to update on

    Raises:
        ClientError: dynamoDB failure
        Exception: raises if invalid field passed
    """
    if any(field not in valid_fields for field in fields):
        raise Exception('Invalid field in: ' + str(fields))

    if 'dob' in fields:
        fields['dob'] = int(time.mktime(datetime.strptime(
            fields['dob'], '%m/%d/%Y').timetuple()))

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
        Key={'id': id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values
    )


def delete_user(id: str):
    """Deletes a user from the users table

    Note: does NOT check whether user actually existed

    Args:
        id (str): user id to delete

    Raises:
        ClientError: dynamoDB failure
    """
    matches = get_matches(id)

    for match in matches:
        remove_match_one_side(match, id)

    users.delete_item(
        Key={'id': id}
    )


def get_matches(id: str) -> List[str]:
    """Get matches for user

    Returns [] if error encountered

    Args:
        id (str): user id to get matches for

    Returns:
        List[str]: list of ids that user is matched to

    Raises:
        ClientError: dynamoDB failure
    """
    response = users.get_item(
        Key={'id': id},
        ProjectionExpression='matches'
    )
    return list(response['Item']['matches']) if 'matches' in response['Item'] else []


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
        ExpressionAttributeValues={':matches': user_1_matches}
    )
    users.update_item(
        Key={'id': user_2},
        UpdateExpression='SET matches = :matches',
        ExpressionAttributeValues={':matches': user_2_matches}
    )


def remove_match_one_side(id: str, match_id: str):
    """Remove match_id from id's matches list

    Args:
        id (str): user id to edit matches for
        match_id (str): user id to remove

    Raises:
        Exception: users not currently matched
        ClientError: dynamoDB failure
    """
    matches = get_matches(id)

    if match_id not in matches:
        raise Exception(
            f"remove match error: {id} not currently matched with {match_id}")

    matches.remove(match_id)

    if matches:
        users.update_item(
            Key={'id': id},
            UpdateExpression='SET matches = :matches',
            ExpressionAttributeValues={':matches': matches}
        )
    else:
        users.update_item(
            Key={'id': id},
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
    response = users.scan(
        Limit=n,
        ProjectionExpression='id,gender,orientation'
    )

    return response['Items'] if 'Items' in response else []
