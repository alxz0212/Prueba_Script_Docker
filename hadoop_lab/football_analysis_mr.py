from mrjob.job import MRJob
from mrjob.step import MRStep
import csv

class MRLaLigaAnalysis(MRJob):

    def steps(self):
        return [
            MRStep(mapper=self.mapper_get_goals,
                   reducer=self.reducer_count_goals)
        ]

    def mapper_get_goals(self, _, line):
        # Ignorar la cabecera si existe
        if "HomeTeam" in line and "AwayTeam" in line:
            return

        # Parsear línea CSV
        # Usamos try-except por seguridad ante líneas mal formadas
        try:
            # El formato del CSV de football-data suele ser:
            # Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,...
            # Pero depende de las columnas que seleccionamos en prepare_data.py
            # ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'Season']
            
            # mrjob lee líneas crudas, así que podemos dividir por coma
            data = list(csv.reader([line]))[0]
            
            # Ajusta estos índices según las columnas que realmente guardaste
            # Hemos guardado: Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,Season
            # Indices:          0     1        2       3    4    5    6
            
            home_team = data[1]
            away_team = data[2]
            home_goals = int(data[3])
            away_goals = int(data[4])
            
            # Emitir (Equipo, Goles) para el local
            yield home_team, home_goals
            # Emitir (Equipo, Goles) para el visitante
            yield away_team, away_goals
            
        except (ValueError, IndexError):
            pass

    def reducer_count_goals(self, team, goals):
        yield team, sum(goals)

if __name__ == '__main__':
    MRLaLigaAnalysis.run()
