import json

import ddbutils
import httputils


def main(event, context):
    print('event:', event)
    print('context:', context)
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is None:
        return httputils.return400()
    terminal_id = queryStringParameters.get('terminal_id', None)
    if terminal_id is None:
        return httputils.return400()
    # 取得
    entry = ddbutils.get_entry(terminal_id)
    if entry is None:
        return httputils.return400()
    # 結果通知
    return {
        'statusCode': 200,
        'body': json.dumps(
            {
                'result': entry.get('status'),
                'match_id': entry.get('match_id')
            }
        )
    }
