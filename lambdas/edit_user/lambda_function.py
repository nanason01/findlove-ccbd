from common.CORS import CORS


@CORS
def lambda_handler(event, _):
    # TODO implement

    print(event)
    return {
        'statusCode': 501,
    }
