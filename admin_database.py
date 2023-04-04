import requests
import json
import argparse

endpoint = 'https://0vhel4c6jg.execute-api.us-east-1.amazonaws.com/prod' + '/admin-database'
api_key = 'A6AtNlhBbl4kpWDSJJCY385okhQ6xgz7fXV56959'


def make_request(type_str: str):
    return requests.post(endpoint, headers={'X-Api-Key': api_key},
                         data=json.dumps({'type': type_str}))


# Parse command line args
parser = argparse.ArgumentParser(description='Process some flags.')

group = parser.add_mutually_exclusive_group(required=True)

group.add_argument('-mock', action='store_true',
                   help='Reset DB with mocked data')
group.add_argument('-reset', action='store_true',
                   help='Reset DB to empty state')

args = parser.parse_args()

if args.mock:
    resp = make_request('MOCK')
    print(resp.headers)
    print(resp.content)
    print(resp)
elif args.reset:
    print(make_request('CLEAR'))
