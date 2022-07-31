from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from django.core import serializers
 
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, StickerSendMessage, LocationSendMessage
import requests
import urllib.request
from index.models import User, Mask
 
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    try:
        handler.handle(
            request.body.decode("utf-8"), request.headers["X-Line-Signature"]
        )
    except InvalidSignatureError:
        raise BadRequest("Invalid request.")
    return HttpResponse("OK")
    # if request.method == 'POST':
    #     signature = request.META['HTTP_X_LINE_SIGNATURE']
    #     body = request.body.decode('utf-8')
 
    #     try:
    #         events = parser.parse(body, signature)  # 傳入的事件
    #     except InvalidSignatureError:
    #         return HttpResponseForbidden()
    #     except LineBotApiError:
    #         return HttpResponseBadRequest()
 
    #     for event in events:
    #         if isinstance(event, MessageEvent):  # 如果有訊息事件
    #             line_bot_api.reply_message(  # 回復傳入的訊息文字
    #                 event.reply_token,
    #                 TextSendMessage(text=event.message.text)
    #             )
    #     return HttpResponse()
    # else:
    #     return HttpResponseBadRequest()

@handler.add(MessageEvent)#, message=TextMessage)
def handle_message(event):
    print(event.source)

    if(event.type == 'message'):
        message = event.message
        print(message)
        if(message.type == 'text'):
            reply = handleText(message, event.reply_token, event.source)
        elif(message.type == 'location'):
            reply = handleLocation(message,event.reply_token,event.source)
        else:
            reply = handleOthers(message,event.reply_token,event.source)
    
    line_bot_api.reply_message(
        event.reply_token,
        reply)

def handleText(message, reply_token, source):
    text_msg = ""

    userID = source.user_id
    print(userID)
    profile = line_bot_api.get_profile(userID)
    userName = profile.display_name
    if(message.text == "查詢據點"):
        text_msg = "請傳送您現在位置~"
    elif(message.text == "查詢點數"):
        userPoint = getUserPoints(userID)
        if(userPoint != -1):
            text_msg = "嗨! " + userName + " 您的累計點數為: " + str(userPoint) + "點"
        else:
            text_msg = "您還未開啟回收口罩之旅喔!"
    else:
        text_msg = userName + "謝謝你~"
    
    return_msg = TextSendMessage(text = text_msg)
    return return_msg

def handleLocation(message, reply_token, source):
    return_msg = []
    address = message.address
    latitude = message.latitude
    longitude = message.longitude
    text_msg = "根據您的目前位置，我們找出以下口罩機據點"
    return_msg.append(TextSendMessage(text=text_msg))
    # locations = maskbase_find(address, latitude, longitude)
    location_message = LocationSendMessage(
            title='日治時期的古蹟',
            address='總統府',
            latitude=25.040213810016002,
            longitude=121.51238385108306
        )
    return_msg.append(location_message)
    return return_msg

def handleOthers(message, reply_token, source):
    sticker_message = StickerSendMessage(
                                    package_id='1',
                                    sticker_id='1'
                                )
    return sticker_message


def getUserPoints(userID):
    try:
        unit = User.objects.get(username = userID)
        return unit.points
    except:
        return -1