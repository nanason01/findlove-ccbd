import json
import boto3

# Create a DynamoDB client
dynamodb = boto3.client('dynamodb')


def reset_tables():
    # Delete "decisions" table if it exists
    try:
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName='decisions')

        response = dynamodb.delete_table(TableName='decisions')

        print("Decisions table deleted successfully!")
    except dynamodb.exceptions.ResourceNotFoundException:
        print("Decisions table does not exist, skipping delete.")

    # Delete "users" table if it exists
    try:
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName='users')

        response = dynamodb.delete_table(TableName='users')

        print("Users table deleted successfully!")
    except dynamodb.exceptions.ResourceNotFoundException:
        print("Users table does not exist, skipping delete.")

    waiter = dynamodb.get_waiter('table_not_exists')
    waiter.wait(TableName='decisions')
    waiter = dynamodb.get_waiter('table_not_exists')
    waiter.wait(TableName='users')

    # Create "candidates" table
    response = dynamodb.create_table(
        TableName='decisions',
        KeySchema=[
            {
                'AttributeName': 'user_id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'candidate_id',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'user_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'candidate_id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    print("Decisions table created successfully!")

    # Create "users" table
    response = dynamodb.create_table(
        TableName='users',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    print("Users table created successfully!")


def fill_sample_data():
    # Create a DynamoDB client
    dynamodb = boto3.client('dynamodb')

    # Sample user data to be inserted into "user_data" table
    users = [
        {"id": "bob", "matches": ["alice"]},
        {"id": "alice", "matches": ["bob"]},
        {"id": "eve", "matches": []},
    ]

    # Sample decisions data to be inserted into "decisions" table
    decisions = [
        {"user_id": "bob", "candidate_id": "alice", "liked": True},
        {"user_id": "alice", "candidate_id": "bob", "liked": True},
        {"user_id": "bob", "candidate_id": "eve", "liked": False},
        {"user_id": "alice", "candidate_id": "eve", "liked": True},
    ]

    waiter = dynamodb.get_waiter('table_exists')
    waiter.wait(TableName='users')

    # Put user data into "user_data" table
    for user in users:

        item = {
            'matches': {'SS': user['matches']}
        } if user['matches'] else {}
        item['id'] = {'S': user['id']}

        response = dynamodb.put_item(
            TableName='users',
            Item=item
        )
        print(response)

    waiter = dynamodb.get_waiter('table_exists')
    waiter.wait(TableName='decisions')

    # Put decisions data into "decisions" table
    for decision in decisions:
        response = dynamodb.put_item(
            TableName='decisions',
            Item={
                'user_id': {'S': decision['user_id']},
                'candidate_id': {'S': decision['candidate_id']},
                'liked': {'BOOL': decision['liked']}
            }
        )
        print(response)


def lambda_handler(event, context):
    if event.get('type') == 'CLEAR':
        reset_tables()
    elif event.get('type') == 'MOCK':
        reset_tables()
        fill_sample_data()
    else:
        return {'statusCode': 404}

    return {'statusCode': 200}
