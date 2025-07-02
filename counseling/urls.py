from django.contrib import admin
from django.urls import path
from . import views


    

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.counseling_form_view, name='counseling_form'),
    path('', views.counseling_form_view, name='counseling_form'),
    path('success/', views.success_view, name='success'),
]

