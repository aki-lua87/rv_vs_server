import uuid
import os

import datautils
import ddbutils
import httputils

from random import randint


def main(event, context):
    print('event:', event)
    weburl = os.environ['OTHELLO_URL']
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is None:
        return httputils.return400()
    terminal_id = queryStringParameters.get('terminal_id', 'anonymous')
    app_id = queryStringParameters.get('app_id', 'anonymous')
    if app_id == 'vrc':
        # プレフィクスとしてIPアドレスを付与
        terminal_id = event.get('requestContext').get('identity').get('sourceIp') + '_' + terminal_id
    # 自身がマッチング中の場合はそのマッチングをキャンセル 対戦相手に通知用の処理
    terminal = ddbutils.get_terminal(terminal_id)
    username = 'anonymous'
    if terminal is not None:
        status = terminal.get('status')
        username = terminal.get('user_name')
        if status == datautils.STATUS_MATCHED:
            ddbutils.match_cancel(terminal.get('match_id'))

    # 待機確認
    stand_by = ddbutils.get_stand_by()
    # webの場合は待機登録ぜずマッチング確認
    if app_id == 'web':
        if stand_by is None:
            print('WEB マッチング無し')
            response = datautils.EntryRegistResponse('invalid', 'none')
            return {
                'headers': {
                    "Access-Control-Allow-Origin": "*"
                },
                'statusCode': 200,
                'body': datautils.responseJson(response)
            }
        else:
            # マッチング
            print('WEB マッチングあり')
            match_id = str(uuid.uuid4())
            terminalA = stand_by.get('attribute_key')
            # 待機相手を削除
            ddbutils.delete_stand_by(terminalA)
            # 先攻後攻を決めるA/Bを入れ替え
            terminalB = terminal_id
            num = randint(0, 11)
            if num < 6:
                terminalA = terminal_id
                terminalB = stand_by.get('attribute_key')
            ddbutils.regist_terminal(terminal_id, ddbutils.makeTTLdays(1), 'web_client')
            ddbutils.regist_match(terminalA, terminalB, match_id)
            response = datautils.EntryRegistResponse(datautils.STATUS_MATCHED, username)
            # マッチング結果通知
            httputils.postWebhook(f'マッチングしたみたい {weburl}kansen?match_id={match_id}')
            return {
                'headers': {
                    "Access-Control-Allow-Origin": "*"
                },
                'statusCode': 200,
                'body': datautils.responseJson(response)
            }
    # 端末が登録されて無い場合は登録
    if terminal is None:
        ddbutils.regist_terminal(terminal_id, ddbutils.makeTTLdays(14), 'anonymous')
    if stand_by is None:
        print('stand_by is None 待機登録')
        # 待機登録
        ddbutils.regist_stand_by(terminal_id)
        ddbutils.update_terminal_entry(terminal_id)
        # 何らかの通知 デバッグ用
        httputils.postWebhook(f'ワールド間対戦オセロでマッチング募集中のユーザがいるかも？ {weburl}')
        # レスポンス
        response = datautils.EntryRegistResponse(datautils.STATUS_ENTRYED, username)
        return httputils.return200response(datautils.responseJson(response))
    # 自身が待機中の場合はマッチングしない
    if stand_by.get('attribute_key') == terminal_id:
        print('待機登録済み')
        ddbutils.update_terminal_entry(terminal_id)  # おそらく不要だが状態遷移のズレがありそうなため追加
        response = datautils.EntryRegistResponse(datautils.STATUS_ENTRYED, username)
        return httputils.return200response(datautils.responseJson(response))
    # マッチング
    match_id = str(uuid.uuid4())
    terminalA = stand_by.get('attribute_key')
    # 待機相手を削除
    ddbutils.delete_stand_by(terminalA)
    terminalB = terminal_id
    # 確率で先行後攻を入れ替える
    num = randint(0, 11)
    if num < 6:
        terminalA = terminal_id
        terminalB = stand_by.get('attribute_key')
    ddbutils.regist_match(terminalA, terminalB, match_id)
    response = datautils.EntryRegistResponse(datautils.STATUS_MATCHED, username)
    print('regist_terminal マッチング')
    print('terminal_id:', terminal_id)
    print('match_id:', match_id)
    httputils.postWebhook(f'マッチングしたみたい {weburl}/kansen?match_id={match_id}')
    # マッチング結果通知
    return httputils.return200response(datautils.responseJson(response))


# 既にマッチング中の場合に呼ばれると上書き
# 進行中放置などのプレイ不可を防ぐために上記のままにする
