from cmath import log
from django.shortcuts import render,HttpResponse
from datetime import datetime
from django.core import serializers
from sqlalchemy import false
from index.models import User
from django.http import JsonResponse
from yoloDetection.Yolo import main, Mask_detection

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

def mask_detect(request):
    mask_obj = Mask_detection()
    score = main(mask_obj, )

    return score

