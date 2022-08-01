from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from django.core import serializers
 
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, StickerSendMessage, LocationSendMessage, QuickReplyButton, QuickReply, MessageAction
import requests
import urllib.request
from index.models import User, MaskBase
 
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
    # print(event.source)

    if(event.type == 'message'):
        message = event.message
        # print(message)
        # if(message.type == 'text' and message.text == "員工註冊"):
        #     pass
        # else:
        character = isStaff(event.source.user_id)
        if(character == 0): # for customer
            if(message.type == 'text'):
                reply = handleCustomerText(message, event.reply_token, event.source)
            elif(message.type == 'location'):
                reply = handleCustomerLocation(message,event.reply_token,event.source)
            else:
                reply = handleOthers(message,event.reply_token,event.source)
        elif(character == 1): # for staff
            if(message.type == 'text'):
                reply = handleStaffText(message, event.reply_token, event.source)
            elif(message.type == 'location'):
                reply = handleStaffLocation(message,event.reply_token,event.source)
            else:
                reply = handleOthers(message,event.reply_token,event.source)
    
    line_bot_api.reply_message(
        event.reply_token,
        reply)
# customers
def handleCustomerText(message, reply_token, source):
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

def handleCustomerLocation(message, reply_token, source):
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

def isStaff(userID):
    try:
        unit = User.objects.get(username = userID)
        return unit.character
    except:
        return -1

# staff
def handleStaffText(message, reply_token, source):
    text_msg = ""

    userID = source.user_id
    # print(userID)
    profile = line_bot_api.get_profile(userID)
    userName = profile.display_name
    if(message.text == "更新據點"):
        return_msg = TextSendMessage(text='請選擇',
                                        quick_reply=QuickReply(items=[
                                            QuickReplyButton(action=MessageAction(label="新增據點", text="新增據點")),
                                            QuickReplyButton(action=MessageAction(label="刪除據點", text="刪除據點")),
                                            QuickReplyButton(action=MessageAction(label="清理據點", text="清理據點"))
                                        ]))
        return return_msg
    elif(message.text == "新增據點"):
        res = updateStaffAction(userID, "create")
        if(res == 1): text_msg = "請傳送您現在位置~"
        else: text_msg = "發生錯誤"
    elif(message.text == "刪除據點"):
        res = updateStaffAction(userID, "delete")
        if(res == 1): text_msg = "請傳送您現在位置~"
        else: text_msg = "發生錯誤"
    elif(message.text == "清理據點"):
        res = updateStaffAction(userID, "cleanup")
        if(res == 1): text_msg = "請傳送您現在位置~"
        else: text_msg = "發生錯誤"
    else:
        text_msg = userName + "謝謝你~"
    
    return_msg = TextSendMessage(text = text_msg)
    return return_msg

def handleStaffLocation(message, reply_token, source):
    userID = source.user_id
    address = message.address
    latitude = message.latitude
    longitude = message.longitude
    current_action =  getStaffAction(userID)
    res = 0
    if(current_action == "create"):
        remain=10
        total_capacity=10
        capability=0
        res = maskbaseInsert(remain, total_capacity, capability, address, latitude, longitude)
    elif(current_action == "delete"):
        res = maskbaseDelete(address)
    elif(current_action == "cleanup"):
        res = maskbaseCleanup(address)

    if(res == -1):
        text_msg = "發生錯誤"
    elif(res == 1):
        text_msg = "更新完成!"
        res = updateStaffAction(userID, "none")
    else:
        text_msg = "請點擊 更新據點按鈕 選擇執行動作~"

    return_msg = TextSendMessage(text = text_msg)
    return return_msg

def updateStaffAction(userID, current_action):
    try:
        User.objects.filter(username=userID).update(current_action=current_action)
    except:
        print("update staff current action error")
        return -1
    return 1

def getStaffAction(userID):
    try:
        unit = User.objects.get(username = userID)
        return unit.current_action
    except:
        return "none"

def maskbaseInsert(remain, total_capacity, capability, address, latitude, longitude):
    try:
        unit = MaskBase.objects.create(remain = remain, total_capacity = total_capacity, capability = capability, address = address, latitude = latitude, longitude = longitude)
        unit.save()
    except:
        print("insert maskbase error")
        return -1
    return 1
    
def maskbaseDelete(address):
    try:
        MaskBase.objects.filter(address = address).delete()
    except:
        print("delete maskbase error")
        return -1
    return 1

def maskbaseCleanup(address):
    try:
        MaskBase.objects.filter(address=address).update(remain = 10, capability = 0)
    except:
        print("clean up maskbase error")
        return -1
    return 1