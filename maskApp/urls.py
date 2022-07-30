"""maskApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from index.views import hello_world, home_page, user_insert,user_update,maskbase_insert,maskbase_update,user_find,user_all,mask_detect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', home_page),
    path('user-insert/', user_insert),
    path('user-update/', user_update),
    path('user-all', user_all),
    path('user-find/<int:id>', user_find, name="user-find"),
    path('maskbase-insert/', maskbase_insert),
    path('maskbase-update/', maskbase_update),
    path('detect/', mask_detect),
    path('masklinebot/', include('masklinebot.urls')) #包含應用程式的網址
]
