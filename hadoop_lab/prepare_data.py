import pandas as pd
import requests
import os
import io

# Configuración
BASE_URL = "https://www.football-data.co.uk/mmz4281"
SEASONS = [
    "2324", "2223", "2122", "2021", "1920", 
    "1819", "1718", "1617", "1516", "1415",
    "1314", "1213", "1112", "1011", "0910"
]
# Guardar en la carpeta 'data' que apunta al SSD
OUTPUT_FILE = "data/laliga_history.csv"

def download_and_merge():
    all_data = []
    print(f"🚀 Iniciando descarga de {len(SEASONS)} temporadas de La Liga...")
    
    for season in SEASONS:
        url = f"{BASE_URL}/{season}/SP1.csv"
        try:
            print(f"   ⬇️ Descargando Temporada {season}...", end="")
            response = requests.get(url)
            response.raise_for_status()
            
            # Leer CSV desde memoria
            # Usar on_bad_lines='skip' o error_bad_lines=False dependiendo de la version de pandas, 
            # pero standard pandas.read_csv suele funcionar bien para estos archivos.
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8', errors='replace')))
            
            # Añadir columna de temporada para referencia
            df['Season'] = season
            
            # Seleccionar columnas clave para reducir tamaño y ruido (opcional, pero recomendado)
            # Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,Season
            # Nuevas métricas: HR(Home Red), AR(Away Red), HY(Home Yellow), AY(Away Yellow)
            cols_of_interest = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'Season', 'HR', 'AR', 'HY', 'AY']
            available_cols = [c for c in cols_of_interest if c in df.columns]
            df = df[available_cols]
            
            all_data.append(df)
            print(" ✅ OK")
            
        except Exception as e:
            print(f" ❌ Error: {e}")

    if all_data:
        print("🔄 Fusionando datos...")
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ ¡Éxito! Archivo generado: {OUTPUT_FILE}")
        print(f"📊 Total de partidos: {len(final_df)}")
        print(f"📂 Guardado en: {os.path.abspath(OUTPUT_FILE)}")
    else:
        print("⚠️ No se pudieron descargar datos.")

if __name__ == "__main__":
    download_and_merge()
