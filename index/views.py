from cmath import log
import os
from django.shortcuts import render,HttpResponse
from datetime import datetime
from django.core import serializers
from index.models import User, Mask
from django.http import JsonResponse
from yoloDetection.Yolo import main, Mask_detection
import cv2 


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
    detection_num = request.GET.get('detection_num')
    mask_obj = Mask_detection()
    source_path = "../../../../Downloads/detection_"+detection_num+".png"
    save_path = "./index/output_image/detection_"+detection_num+".jpg"
    score = main(mask_obj, source_path, save_path)
    os.remove("../../../../Downloads/detection_"+detection_num+".png")
    return JsonResponse({0: score}, safe=False)


# def camera_capture():
#     cam = cv2.VideoCapture(0)
#     cv2.namedWindow("test")
#     img_counter = 0
#     while True:
#         ret, frame = cam.read()
#         if not ret:
#             print("failed to grab frame")
#             break
#         cv2.imshow("test", frame)
#         k = cv2.waitKey(1)
#         if k%256 == 27: # ESC pressed
#             print("Escape hit, closing...")
#             break
#         elif k%256 == 32: # SPACE pressed
#             img_name = "opencv_frame_{}.png".format(img_counter)
#             cv2.imwrite(img_name, frame)
#             print("{} written!".format(img_name))
#             img_counter += 1
#     cam.release()
#     cv2.destroyAllWindows()

