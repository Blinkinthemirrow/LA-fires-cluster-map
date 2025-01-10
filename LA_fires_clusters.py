import pandas as pd
import folium
from folium.plugins import MarkerCluster
import requests
from io import BytesIO

# URL вашего файла на GitHub
INPUT_FILE = "https://raw.githubusercontent.com/Blinkinthemirrow/LA-fires-cluster-map/main/LA_fires.xlsx"

# Загрузка файла с GitHub
response = requests.get(INPUT_FILE)
response.raise_for_status()  # Проверяем, что файл успешно загружен

# Чтение Excel-файла в pandas
fires_data = pd.read_excel(BytesIO(response.content))

# Оставляем нужные колонки
fires_cleaned = fires_data[['incident_date_created', 'incident_longitude', 'incident_latitude']].copy()
fires_cleaned.rename(columns={
    'incident_date_created': 'date',
    'incident_longitude': 'longitude',
    'incident_latitude': 'latitude'
}, inplace=True)

# Преобразуем даты
fires_cleaned['date'] = pd.to_datetime(fires_cleaned['date'], errors='coerce')
fires_cleaned.dropna(subset=['longitude', 'latitude', 'date'], inplace=True)

# Создание карты
fire_map_clustered = folium.Map(location=[fires_cleaned['latitude'].mean(), fires_cleaned['longitude'].mean()], zoom_start=6)

# Создание слоя с кластерами
marker_cluster = MarkerCluster().add_to(fire_map_clustered)

# Добавление точек на карту
for _, row in fires_cleaned.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"Date: {row['date'].strftime('%Y-%m-%d')}",
    ).add_to(marker_cluster)

# Сохранение карты
OUTPUT_FILE_CLUSTER = "fire_cluster_map.html"
fire_map_clustered.save(OUTPUT_FILE_CLUSTER)
print(f"Интерактивная карта с кластерами создана: {OUTPUT_FILE_CLUSTER}")
