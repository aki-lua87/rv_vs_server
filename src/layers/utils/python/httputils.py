import json


def return400(message='bad request'):
    return {
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 400,
        'body': json.dumps(
            {
                'result': 'ERROR',
                'error': message
            }
        )
    }


def return200():
    return {
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 200,
        'body': json.dumps(
            {
                'result': 'OK'
            }
        )
    }


# クライアントでキャンセルを取得したい場合のみ使用
def return200canncel():
    return {
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 200,
        'body': json.dumps(
            {
                'status': 'CANCELED'
            }
        )
    }


def return200response(responseJson):
    return {
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 200,
        'body': responseJson
    }
