"""medical_blockchain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home),
    path('block1/',views.block1),
    path('loginD/',views.Dlogin),
    path('loginch/',views.loginch),
    path('fetch/',views.fetch),
    path('signup/',views.signup),
    path('savedata/',views.savedata),
    path('upload-csv/',views.upload),
    path('checkpatient/',views.checkpatient),
    path('savefile/', views.uploadfile),
    path('block/',views.block),
    path('blk/',views.blk),
    path('down/',views.download),
    path('feedbackform/',views.feedbackform),
    path('healthprediction/',views.healthpredict),
    path('health/',views.health),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
