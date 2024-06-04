# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# urls.py

from django.urls import path, re_path
from apps.home import views

urlpatterns = [
    path('', views.index, name='home'),
    path('precipitation_predictions/', views.precipitation_predictions, name='precipitation_predictions'),
    path('charte_station/', views.charte_station, name='charte_station'),
    re_path(r'^.*\.*', views.pages, name='pages'),
]

