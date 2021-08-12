from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import time
import random
#======python的函數庫===========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi('Lcnf7KIjaTuWednr4wakRFNlwqzFHlIe/XqeIFqW0Y0E4PlQxIUoreX1WENUiHxDRgVDZsd11iE+wds4ggKQ6Fovq/2jVBC+NBxWh98vGTwVZteYlLPj9uH8V9q87GsdlfWybVvKxumlFvq3Cl6/yQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('7abfbc51de78526242d0d2070b94bde3')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
class Data():
    def __init__(self):
        self.player = []
        self.state = 'none' # none->gaming
        self.guess = []
        self.rf = []
        self.ans = ''
        self.fourorsix = 4
    def reset(self):
        self.guess = []
        self.rf = []
        self.ans = ''
        self.fourorsix = 4

data = Data()

def Verify(func):
    def wrapper(**kwargs):
        user_id = kwargs['user_id']
        if user_id not in data.player:
            return TextSendMessage(text='不是玩家')
        else:
            return func(**kwargs)
    return wrapper

def IsState(states=None):
    def decorator(func):
        def wrapper(**kwargs):
            data = kwargs['data']
            if data.state not in states:
                return TextSendMessage(text='遊戲已經開始囉')
            else:
                return func(**kwargs)
        return wrapper
    return decorator

@IsState(states = ['none'])
def CreateGameFor46(data=None, user_id=None):
    data.state = 'gaming'
    data.player.append(user_id)
    buttons = ButtonsTemplate(
        title = '要玩4碼還是6碼?',
        text = '4 or 6',
        actions = [
            MessageTemplateAction(
                label = '4碼',
                text = '4碼'
            ),
            MessageTemplateAction(
                label = '6碼',
                text = '6碼'
            )
        ]
    )
    return TemplateSendMessage(alt_text="要玩4碼還是6碼?", template=buttons)

@Verify
@IsState(states = ['gaming'])
def CreateGame(msg=None, data=None, user_id=None):
    n = int(msg[0])
    data.fourorsix = n
    box = ['0','1','2','3','4','5','6','7','8','9']
    ans = ''
    r = 9
    for i in range(n):
        index = random.randint(0, r)
        ans += box[index]
        box.pop(index)
        r -= 1
    data.ans = ans
    return TextSendMessage(text='請輸入'+str(n)+'碼不同的數字')

@Verify
@IsState(states = ['gaming'])
def AgainGame(data=None, user_id=None):
    data.reset()
    buttons = ButtonsTemplate(
        title = '要玩4碼還是6碼?',
        text = '4 or 6',
        actions = [
            MessageTemplateAction(
                label = '4碼',
                text = '4碼'
            ),
            MessageTemplateAction(
                label = '6碼',
                text = '6碼'
            )
        ]
    )
    return TemplateSendMessage(alt_text="要玩4碼還是6碼?", template=buttons)

@Verify
@IsState(states = ['gaming'])
def EndGame(data=None, user_id=None):
    data.player = data.player[:1]
    data.state = 'none'
    data.reset()
    return TextSendMessage(text='感謝遊玩')

@Verify
def ForceClose(data=None, user_id=None):
    data.player = data.player[:1]
    data.state = 'none'
    data.reset()
    return TextSendMessage(text='已清空')

@Verify
@IsState(states = ['gaming'])
def Check(msg=None, data=None, user_id=None):
    ans = data.ans
    n = data.fourorsix
    AplusB = 0
    A = 0
    for i in range(n):
        if msg[i] == ans[i]:
            A += 1
    if A == n:
        buttons = ButtonsTemplate(
            title = '恭喜答對，你總共猜了'+str(len(data.rf)+1)+'次',
            text = '還要繼續玩嗎?',
            actions = [
                MessageTemplateAction(
                    label = '要',
                    text = '要'
                ),
                MessageTemplateAction(
                    label = '不要',
                    text = '不要'
                )
            ]
        )
        return TemplateSendMessage(alt_text="繼續與否", template=buttons)
    for i in ans:
        for j in msg:
            if j == i:
                AplusB += 1
    txt = str(A)+'A'+str(AplusB-A)+'B'
    data.guess.append(msg)
    data.rf.append(txt)
    return TextSendMessage(text=txt)

@Verify
@IsState(states = ['gaming'])
def CheckHistory(data=None, user_id=None):
    rf =  data.rf
    guess = data.guess
    txt = ''
    for i in range(len(rf)):
        if i == len(rf) - 1:
            onehist = guess[i] + ' ' + rf[i]
        else:
            onehist = guess[i] + ' ' + rf[i] + '\n'
        txt += onehist
    return TextSendMessage(text=txt)

@Verify
@IsState(states = ['gaming'])
def CheckAns(data=None, user_id=None):
    buttons = ButtonsTemplate(
        title = '答案是'+data.ans,
        text = '要重玩嗎?',
        actions = [
            MessageTemplateAction(
                label = '重來',
                text = '重來'
            ),
            MessageTemplateAction(
                label = '不玩了',
                text = '不玩了'
            )
        ]
    )
    return TemplateSendMessage(alt_text="重來與否", template=buttons)

@IsState(states = ['none'])
def God(data=None, user_id=None):
    data.player.append(user_id)
    return TextSendMessage(text='你是管理員')
# 處理回傳
@handler.add(PostbackEvent)
def handle_postback(event):
    msg = event.postback.data
    user_id = event.source.user_id
    line_bot_api.reply_message(event.reply_token, message)

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    user_id = event.source.user_id
    if msg == '開始':
        message = CreateGameFor46(data=data, user_id=user_id)
        line_bot_api.reply_message(event.reply_token, message)

    if msg == '4碼' or msg == '6碼':
        message = CreateGame(msg=msg, data=data, user_id=user_id)
        line_bot_api.reply_message(event.reply_token, message)

    if len(msg) == data.fourorsix:
        box = '0123456789'
        b = 1
        for i in range(data.fourorsix):
            if msg[i] in box:
                box = box.replace(msg[i],'')
            else:
                b = 0
        if b:
            message = Check(msg=msg, data=data, user_id=user_id)
            line_bot_api.reply_message(event.reply_token, message)

    if msg == '過程':
        message = CheckHistory(data=data, user_id=user_id)
        line_bot_api.reply_message(event.reply_token, message)

    if msg == '要' or msg == '重來':
        message = AgainGame(data=data, user_id=user_id)
        line_bot_api.reply_message(event.reply_token, message)

    if msg == '不要' or msg == '不玩了':
        message = EndGame(data=data, user_id=user_id)
        line_bot_api.reply_message(event.reply_token, message)

    if msg == '看答案':
        message = CheckAns(data=data, user_id=user_id)
        line_bot_api.reply_message(event.reply_token, message)

    if msg == '清空':
        message = ForceClose(data=data, user_id=user_id)
        line_bot_api.reply_message(event.reply_token, message)

    if msg == '上帝':
        message = God(data=data, user_id=user_id)
        line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
# git add .
# git commit -m "a"
# git push heroku master
