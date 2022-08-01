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
from math import radians,cos,sin,asin,sqrt
 
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
        text_msg = userName + "謝謝你~目前不為您提供此服務。"
    
    return_msg = TextSendMessage(text = text_msg)
    return return_msg

def handleCustomerLocation(message, reply_token, source):
    return_msg = []
    address = message.address
    latitude = message.latitude
    longitude = message.longitude
    
    maskbaseList = getMaskbases(1)
    nearMaskbaseList = []
    # nearMaskbaseList = calculateDistance(maskbsaeList, address, latitude, longitude)
    for maskbase in maskbaseList:
        dis = haversine(longitude, latitude, maskbase.longitude, maskbase.latitude)
        print(dis)
        if(dis <= 10): 
            nearMaskbaseList.append(maskbase)

    if(nearMaskbaseList == []):
        text_msg = "目前沒有距離較近且可使用的口罩回收服務據點"
        return_msg = TextSendMessage(text = text_msg)
    else:
        text_msg = "目前有以下口罩回收據點可使用"
        return_msg.append(TextSendMessage(text=text_msg))
        for maskbase in nearMaskbaseList:
            # print(maskbase.id ,maskbase.address, maskbase.latitude, maskbase.longitude)
            location_message = LocationSendMessage(
                        title='據點'+str(maskbase.id),
                        address=maskbase.address,
                        latitude=maskbase.latitude,
                        longitude=maskbase.longitude
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
    return_msg = []
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
        if(res == 1): text_msg = "請傳送據點位置~"
        else: text_msg = "發生錯誤"
    elif(message.text == "刪除據點"):
        res = updateStaffAction(userID, "delete")
        if(res == 1): text_msg = "請傳送據點位置~"
        else: text_msg = "發生錯誤"
    elif(message.text == "清理據點"):
        res = updateStaffAction(userID, "cleanup")
        if(res == 1): text_msg = "請傳送據點位置~"
        else: text_msg = "發生錯誤"
    elif(message.text == "查看需清空的據點"):
        maskbaseList = getFullMaskbases(0)
        if(maskbaseList == "none"):
            text_msg = "目前沒有需要清空的據點"
            return_msg = TextSendMessage(text = text_msg)
        else:
            text_msg = "目前有以下據點需清空"
            return_msg.append(TextSendMessage(text=text_msg))
            for maskbase in maskbaseList:
                # print(maskbase.id ,maskbase.address, maskbase.latitude, maskbase.longitude)
                location_message = LocationSendMessage(
                            title='據點'+str(maskbase.id),
                            address=maskbase.address,
                            latitude=maskbase.latitude,
                            longitude=maskbase.longitude
                        )
                return_msg.append(location_message)
        return return_msg
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
        capability=1
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
        MaskBase.objects.filter(address=address).update(remain = 10, capability = 1)
    except:
        print("clean up maskbase error")
        return -1
    return 1
    
def getMaskbases(capability):
    try:
        units = MaskBase.objects.filter(capability = capability)
        return units
    except:
        print("get full maskbases error")
        return "none"

#根據經緯度計算兩點距離
def haversine(lon1,lat1,lon2,lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # 將十進制度數轉化為弧度
    print(lon1, lat1, lon2, lat2)
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球平均半徑，單位為公里
    return c * r 