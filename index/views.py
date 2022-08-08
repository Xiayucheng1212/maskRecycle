from cmath import log
import os
from django.shortcuts import render,HttpResponse
from datetime import datetime
from django.core import serializers
from parso import parse
from sqlalchemy import null
from index.models import User, Mask
from django.http import JsonResponse
from yoloDetection.Yolo import main, Mask_detection
from bluetooth import bluetooth
import threading
bt = null
def hello_world(request):
    return render(request, 'hello_world.html', {
        'current_time': str(datetime.now()),
    })

def home_page(request):
    return render(request, 'index.html')

def user_all(request):
    try: 
        unit = User.objects.all().order_by('id') 
        unit_serialized = serializers.serialize("json", unit)
    except:
        errormessage = " (讀取錯誤!)"
        log(errormessage)
    return JsonResponse(unit_serialized, safe=False)

def user_insert(request): # only use form-data when POST
    username = request.POST.get('username')
    password = request.POST.get('password')
    unit = User.objects.create(username = username, password = password, points=0)
    unit.save()
    unit_id = User.objects.get(username=username, password=password).id
    return JsonResponse(unit_id, safe=False)

def user_find(request,id):
    if id:
        unit = User.objects.get(id = id)
        return JsonResponse({'username': unit.username, 'points': unit.points}, safe=False)
    else:
        return JsonResponse({}, safe=False)

def user_update(request):
    
    return
def maskbase_insert(request):
    name = request.POST.get('name')
    remain = request.POST.get('remain')
    total_capacity = request.POST.get('total_capacity')
    capability = request.POST.get('capability')
    unit = User.objects.create(name = name, remain = remain, total_capacity = total_capacity, capability = capability)
    unit.save()
    unit_id = User.objects.get(name = name).id
    return JsonResponse(unit_id, safe=False)
def maskbase_update():
    return

def add_points(request): # id, points_num GET
    return render(request, 'add_points_success.html', {}) #points username

def transmitOperation(flag: str): #f: start, p: stop
    bt = bluetooth("/dev/tty.HC-06-SerialPort")
    while not bt.is_open(): pass
    print("BT Connected!")

    def read():
        while True:
            if bt.waiting():
                print(bt.readString())

    readThread = threading.Thread(target=read)
    readThread.setDaemon(True)
    readThread.start()
    bt.write(flag) # f: start moving, p: stop moving
    return flag

def mask_detect(request):
    detection_num = request.GET.get('detection_num')
    mask_obj = Mask_detection()
    source_path = "../../../../Downloads/detection_"+detection_num+".png"
    save_path = "./index/output_image/detection_"+detection_num+".jpg"
    score = main(mask_obj, source_path, save_path)
    os.remove("../../../../Downloads/detection_"+detection_num+".png")
    print(score)
    # if int(score) >= 0.8: #threshold = 0.8 
        # transmitOperation("f")
    return JsonResponse({0: score}, safe=False)

def transmit_stop(request):
    transmitOperation('p')
    return JsonResponse({0: True}, safe=False)

def transmit_start(request):
    transmitOperation('f')
    return JsonResponse({0: True}, safe=False)

def transmit_exit(request):
    transmitOperation('exit')
    return JsonResponse({0:True}, safe=False)