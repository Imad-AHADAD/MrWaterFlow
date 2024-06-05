from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
import pandas as pd
import plotly.express as px
import plotly.io as pio
from django import template
from django.core.cache import cache
from datetime import datetime, timedelta
import pickle
import numpy as np


# Global variable to store the dataset
dataset = None

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    return render(request, 'home/index.html', context)

@login_required(login_url="/login/")
def pages(request):
    context = {}
    try:
        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        return render(request, 'home/' + load_template, context)
    except template.TemplateDoesNotExist:
        return render(request, 'home/page-404.html', context)
    #except Exception as e:
     #   return render(request, 'home/page-500.html', context)

@login_required(login_url="/login/")
def precipitation_predictions(request):
    global dataset

    # Load the dataset if not already loaded
    if dataset is None:
        file_path = 'apps/static/assets/dataset/water_dataset_v2.csv'
        try:
            dataset = pd.read_csv(file_path)
            print("Fichier Excel chargé avec succès")
        except Exception as e:
            print(f"Erreur lors du chargement du fichier Excel: {e}")
            return render(request, 'home/precipitations.html', {'graph_html': ''})

    # Filter data based on user input
    station_name = request.GET.get('station_name')
    df = dataset.copy()

    if station_name:
        df = df[df['NAME'] == station_name]

    # Create Plotly figure
    fig = px.line(df, x='DATE', y='PRCP', title=f'Précipitations en fonction de temps de la station {station_name}')
    graph_html = pio.to_html(fig, full_html=False)

    return render(request, 'home/precipitations.html', {'graph_html': graph_html})


@login_required(login_url="/login/")
def charte_station(request):
    global dataset

    # Load the dataset if not already loaded
    if dataset is None:
        file_path = 'apps/static/assets/dataset/water_dataset_v2.csv'
        try:
            dataset = pd.read_csv(file_path)
            print("Fichier Excel chargé avec succès")
        except Exception as e:
            print(f"Erreur lors du chargement du fichier Excel: {e}")
            return render(request, 'home/visualisation.html', {'graph_html': ''})

    # Filtrer les données pour les colonnes nécessaires
    stations = dataset[['NAME', 'LATITUDE', 'LONGITUDE']].drop_duplicates()

    # Créer une carte des stations météorologiques
    fig_map = px.scatter_geo(stations,
                            lat='LATITUDE',
                            lon='LONGITUDE',
                            hover_name='NAME',
                            title='Carte des Stations Météorologiques au Maroc')
    graph_html = pio.to_html(fig_map, full_html=False)

    return render(request, 'home/visualisation.html', {'graph_html': graph_html})


@login_required(login_url="/login/")
def precipitation_data(request):
    global dataset

    # Load the dataset if not already loaded
    if dataset is None:
        file_path = 'apps/static/assets/dataset/water_dataset_v2.csv'
        try:
            dataset = pd.read_csv(file_path)
            print("Fichier CSV chargé avec succès")
        except Exception as e:
            print(f"Erreur lors du chargement du fichier Excel: {e}")
            return render(request, 'home/dataset.html', {'data': []})

    # Get the first 50 rows of the dataset
    data_records = dataset.head(1000).to_dict('records')

    # Render the template with the data
    return render(request, 'home/dataset.html', {'data': data_records})






# Load the scaler and model
scaler_filename = r'apps\static\assets\model\scaler.pkl'
model_filename = r'apps\static\assets\model\prcp_lr_model.pkl'

with open(scaler_filename, 'rb') as file:
        scaler = pickle.load(file)

with open(model_filename, 'rb') as file:
        model = pickle.load(file)

# Station data
station_data = {
        "MELILLA, SP": {"latitude": 35.2778, "longitude": -2.9553, "elevation": 47},
        "BASSATINE, MO": {"latitude": 33.879, "longitude": -5.515, "elevation": 576.1},
        "SALE, MO": {"latitude": 34.051, "longitude": -6.752, "elevation": 84.1},
        "OUARZAZATE, MO": {"latitude": 30.93, "longitude": -6.9, "elevation": 1139},
        "NOUASSEUR, MO": {"latitude": 33.367, "longitude": -7.583, "elevation": 206},
        "KENITRA PORT LYAUTEY, MO": {"latitude": 34.3, "longitude": -6.6, "elevation": 12.2},
        "MENARA, MO": {"latitude": 31.607, "longitude": -8.036, "elevation": 467.9},
        "ESSAOUIRA, MO": {"latitude": 31.398, "longitude": -9.682, "elevation": 117},
        "MIDELT, MO": {"latitude": 32.68, "longitude": -4.73, "elevation": 1508},
        "ANFA, MO": {"latitude": 33.557, "longitude": -7.66, "elevation": 61.9},
        "OUJDA, MO": {"latitude": 34.78, "longitude": -1.93, "elevation": 468},
        "TANGIER CITY, MO": {"latitude": 35.78, "longitude": -5.82, "elevation": 86},
        "SANIAT RMEL, MO": {"latitude": 35.594, "longitude": -5.32, "elevation": 3},
}
def predictions(request):

    station_name = request.GET.get('station_name', 'MELILLA, SP')
    station_info = station_data.get(station_name)

    if station_info:
        latitude = station_info['latitude']
        longitude = station_info['longitude']
        elevation = station_info['elevation']

        start_date = datetime(2024, 6, 1)
        end_date = datetime(2024, 7, 31)
        date_generated = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

        predictions = []
        for date in date_generated:
            user_input_df = pd.DataFrame({
                'LATITUDE': [latitude],
                'LONGITUDE': [longitude],
                'ELEVATION': [elevation],
                'YEAR': [date.year],
                'MONTH': [date.month],
                'DAY': [date.day]
            })

            user_input_scaled = scaler.transform(user_input_df)
            predicted_prcp = model.predict(user_input_scaled)
            predictions.append({"date": date, "prcp": predicted_prcp[0]})

        df_predictions = pd.DataFrame(predictions)

        # Visualization
        fig = px.line(df_predictions, x='date', y='prcp', title=f'Prédictions des Précipitations pour {station_name}')
        graph_html = fig.to_html(full_html=False)

        return render(request, 'home/predictions.html', {'graph_html': graph_html})
    else:
        return render(request, 'home/predictions.html', {'graph_html': 'Station not found.'})




def specific_prediction_view(request):
    if request.method == "GET":
        station_name = request.GET.get('station_name', 'MELILLA, SP')
        year = int(request.GET.get('year', 2024))
        month = int(request.GET.get('month', 6))
        day = int(request.GET.get('day', 1))

        station_info = station_data.get(station_name)

        if station_info:
            latitude = station_info['latitude']
            longitude = station_info['longitude']
            elevation = station_info['elevation']

            user_input_df = pd.DataFrame({
                'LATITUDE': [latitude],
                'LONGITUDE': [longitude],
                'ELEVATION': [elevation],
                'YEAR': [year],
                'MONTH': [month],
                'DAY': [day]
            })

            user_input_scaled = scaler.transform(user_input_df)
            predicted_prcp = model.predict(user_input_scaled)[0]

            return render(request, 'home/predictions.html', {'predicted_prcp': predicted_prcp})

    return render(request, 'home/predictions.html', {'predicted_prcp': None})