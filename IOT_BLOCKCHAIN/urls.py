"""
URL configuration for IOT_BLOCKCHAIN project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('data_access/', views.data_access, name='data_access'),
    path('data_storage/', views.data_storage, name='data_storage'),
    path("store/custom/", views.custom_data_storage, name="custom_data_storage"),
    path("generate-random/", views.generate_random_data, name="generate_random_data"),
    path("view-record/<str:cid>/", views.view_record),
    path("decrypt-record/", views.decrypt_record),
    path("store-random-data/", views.store_random_data, name="store_random_data"),
]
