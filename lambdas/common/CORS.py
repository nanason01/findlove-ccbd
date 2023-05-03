CORS_headers = {
    'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': True,
        'Content-Type': 'application/json',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': '*',
    }
}


def CORS(lambda_handler):
    def add_cors(event, context):
        return {
            **CORS_headers,
            **lambda_handler(event, context),
        }

    return add_cors
