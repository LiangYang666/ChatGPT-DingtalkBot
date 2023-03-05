import json
import hmac
import hashlib
import base64
import requests
from flask import Flask, request
import openai
from LRU_cache import LRUCache
import os
import threading
from collections import deque

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

openai.api_key = ""
app_secret = ""


all_chat_dict = LRUCache(20)
lock = threading.Lock()


def get_chat_response(chat_info, message):
    chat_with_history = chat_info["chat_with_history"]
    messages_history = chat_info["messages_history"]
    if not chat_with_history:
        messages_history.clear()
    messages_history.append({"role": "user", "content": message})
    print("调用ChatGPT API提问")
    print(messages_history)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=list(messages_history)
    )
    if completion.get("error"):
        return "出错"
    data = completion.choices[0].message.content.strip()
    if chat_with_history:
        messages_history.append({"role": "assistant", "content": data})

    return data


app = Flask(__name__)


# 发送markdown消息
def send_msg_by_bot(userid, message, webhook_url):
    '''
    userid: @用户 钉钉id
    title : 消息标题
    message: 消息主体内容
    webhook_url: 通讯url
    '''
    data = {
        "at": {
            "atUserIds":[
                
            ],
            "isAtAll": False
        },
        "msgtype": "text",
        "text": {
            "content": "@"+userid+"\n"+message  # 消息主体内容
        }
    }
    print("通过机器人将消息发回")
    # 利用requests发送post请求
    req = requests.post(webhook_url, json=data)


# 消息数字签名计算核对
def check_sig(timestamp):
    app_secret_enc = app_secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, app_secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


@app.route("/", methods=["POST"])
def get_data():
    # 第一步验证：是否是post请求
    if request.method == "POST":
        # print(request.headers)
        # 签名验证 获取headers中的Timestamp和Sign
        timestamp = request.headers.get('Timestamp')
        sign = request.headers.get('Sign')
        # 第二步验证：签名是否有效
        if check_sig(timestamp) == sign:
            # 获取、处理数据
            req_data = json.loads(str(request.data, 'utf-8'))
            # print(req_data)
            # 调用数据处理函数
            handle_info(req_data)
            print('验证通过')
            return 'hhh'

        print('验证不通过')
        return 'ppp'

    print('有get请求')
    return 'sss'


# 处理自动回复消息
def handle_info(req_data):
    # 解析用户发送消息 通讯webhook_url
    text_info = req_data['text']['content'].strip()
    webhook_url = req_data['sessionWebhook']
    sender_nick = req_data['senderNick']
    sender_id = req_data['senderId']

    chat_id = sender_id+webhook_url
    lock.acquire()
    if chat_id not in all_chat_dict:
        chat_info = {"chat_with_history": False, "messages_history": deque(maxlen=7)}
        all_chat_dict.put(chat_id, chat_info)
    else:
        chat_info = all_chat_dict.get(chat_id)       # TODO 流转下去但可能会被LRU删掉
    lock.release()

    messages_history = chat_info["messages_history"]

    if text_info == '帮助':
        msg = '含如下指令\n ' \
              '1.开始聊天：开始普通聊天，不结合历史聊天记录\n ' \
              '2.开始串聊：开始串聊，结合历史聊天记录\n ' \
              '3.重置：重置聊天，清空之前的聊天记录\n' \
              '\ncode from https://github.com/LiangYang666/DingtalkBot-ChatGPT-API-Python'
        send_msg_by_bot(sender_nick, msg, webhook_url)
    elif text_info == '开始聊天':
        chat_info["chat_with_history"] = False
        send_msg_by_bot(sender_nick, "开始普通聊天，不结合历史聊天记录", webhook_url)
    elif text_info == '重置':
        messages_history.clear()
        send_msg_by_bot(sender_nick, "已重置聊天记录，开始聊天吧", webhook_url)
    elif text_info == '开始串聊':
        chat_info["chat_with_history"] = True
        send_msg_by_bot(sender_nick, "开始聊天，从现在开始结合最近7条历史聊天记录", webhook_url)
    else:

        rs = get_chat_response(chat_info, text_info)
        send_msg_by_bot(sender_nick, rs, webhook_url)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8011, debug=True)
