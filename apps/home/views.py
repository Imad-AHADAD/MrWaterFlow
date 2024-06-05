from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
import pandas as pd
import plotly.express as px
import plotly.io as pio
from django import template
from django.core.cache import cache



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
    fig = px.line(df, x='DATE', y='PRCP', title='Précipitations Over Time')
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
