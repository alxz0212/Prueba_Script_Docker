from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, desc, count

def main():
    # Inicializar la sesión de Spark conectando al clúster master
    spark = SparkSession.builder \
        .appName("LaLigaSparkSQL_Advanced") \
        .master("spark://spark-master:7077") \
        .getOrCreate()

    # Cargar los datos (el CSV generado por prepare_data.py)
    # Nota: la ruta debe ser la del contenedor
    csv_path = "/opt/spark/scripts/laliga_history.csv"
    
    print(f"\n[SPARK] Cargando datos desde: {csv_path}...")
    
    df = spark.read.csv(csv_path, header=True, inferSchema=True)

    # Registrar como Tabla Temporal para usar SQL puro (estilo Hive)
    df.createOrReplaceTempView("laliga_stats")

    print("\n" + "="*50)
    print("EJECUTANDO CONSULTAS SQL (Estilo Apache Hive)")
    print("="*50)

    # 1. Top 10 Equipos con más Goles (Usando SQL)
    print("\n--- [SQL] Top 10 Equipos por Goles Totales ---")
    top_goles = spark.sql("""
        SELECT Team, SUM(goals) as Total_Goles
        FROM (
            SELECT HomeTeam as Team, FTHG as goals FROM laliga_stats
            UNION ALL
            SELECT AwayTeam as Team, FTAG as goals FROM laliga_stats
        )
        GROUP BY Team
        ORDER BY Total_Goles DESC
        LIMIT 10
    """)
    top_goles.show()

    # 2. Top 5 Equipos con más Tarjetas Rojas (Usando SQL)
    print("\n--- [SQL] Top 5 Equipos con más Tarjetas Rojas ---")
    top_rojas = spark.sql("""
        SELECT Team, SUM(reds) as Total_Rojas
        FROM (
            SELECT HomeTeam as Team, HR as reds FROM laliga_stats
            UNION ALL
            SELECT AwayTeam as Team, AR as reds FROM laliga_stats
        )
        GROUP BY Team
        ORDER BY Total_Rojas DESC
        LIMIT 5
    """)
    top_rojas.show()

    # 3. Eficiencia: Victorias vs Partidos Jugados
    print("\n--- [SQL] Eficiencia de Victorias (%) ---")
    eficiencia = spark.sql("""
        SELECT Team, 
               COUNT(*) as Partidos, 
               SUM(CASE WHEN Winner = Team THEN 1 ELSE 0 END) as Victorias,
               ROUND((SUM(CASE WHEN Winner = Team THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) as Eficiencia_Pct
        FROM (
            SELECT HomeTeam as Team, FTR, CASE WHEN FTR = 'H' THEN HomeTeam WHEN FTR = 'A' THEN AwayTeam ELSE 'Empate' END as Winner FROM laliga_stats
            UNION ALL
            SELECT AwayTeam as Team, FTR, CASE WHEN FTR = 'H' THEN HomeTeam WHEN FTR = 'A' THEN AwayTeam ELSE 'Empate' END as Winner FROM laliga_stats
        )
        GROUP BY Team
        HAVING COUNT(*) > 50
        ORDER BY Eficiencia_Pct DESC
        LIMIT 10
    """)
    eficiencia.show()

    # 4. CONSULTA COMPLEJA: "Especialistas en ganar fuera de casa" (Away Efficiency)
    print("\n--- [SQL COMPLEJO] Top 5 Visitantes más peligrosos (Eficiencia Fuera) ---")
    away_specialists = spark.sql("""
        SELECT AwayTeam as Equipo,
               COUNT(*) as Partidos_Fuera,
               SUM(CASE WHEN FTR = 'A' THEN 1 ELSE 0 END) as Victorias_Fuera,
               ROUND((SUM(CASE WHEN FTR = 'A' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) as Eficiencia_Fuera_Pct
        FROM laliga_stats
        GROUP BY AwayTeam
        HAVING COUNT(*) > 30
        ORDER BY Eficiencia_Fuera_Pct DESC
        LIMIT 5
    """)
    away_specialists.show()

    # 5. CONSULTA COMPLEJA: Evolución de goles por Temporada
    print("\n--- [SQL COMPLEJO] Evolución de Goles Totales por Temporada ---")
    season_evolution = spark.sql("""
        SELECT Season,
               SUM(FTHG + FTAG) as Goles_Totales,
               ROUND(AVG(FTHG + FTAG), 2) as Promedio_Por_Partido
        FROM laliga_stats
        GROUP BY Season
        ORDER BY Goles_Totales DESC
    """)
    season_evolution.show(20)

    spark.stop()

if __name__ == "__main__":
    main()
