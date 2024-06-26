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
    path('predictions/', views.predictions, name='predictions'),
    path('specific_prediction_view/', views.specific_prediction_view, name='specific_prediction_view'),
    path('charte_station/', views.charte_station, name='charte_station'),
    path('precipitation_data/', views.precipitation_data, name='precipitation_data'),   
    re_path(r'^.*\.*', views.pages, name='pages'),

]

