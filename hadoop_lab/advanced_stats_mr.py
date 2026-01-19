from mrjob.job import MRJob
from mrjob.step import MRStep
import csv

class MRAdvancedLaLiga(MRJob):

    def steps(self):
        return [
            MRStep(mapper=self.mapper_extract_stats,
                   reducer=self.reducer_aggregate_stats)
        ]

    def mapper_extract_stats(self, _, line):
        if "HomeTeam" in line and "AwayTeam" in line:
            return

        try:
            # Columns: Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,Season,HR,AR,HY,AY
            # Index:   0    1        2        3    4    5   6      7  8  9  10
            data = list(csv.reader([line]))[0]
            
            home = data[1]
            away = data[2]
            
            h_goals = int(data[3])
            a_goals = int(data[4])
            result = data[5]
            
            # Cards (Handle empty strings if data missing)
            h_red = int(data[7]) if data[7] else 0
            a_red = int(data[8]) if data[8] else 0
            h_yellow = int(data[9]) if data[9] else 0
            a_yellow = int(data[10]) if data[10] else 0
            
            h_win = 1 if result == 'H' else 0
            a_win = 1 if result == 'A' else 0
            
            # Emitir estadísticas (Nombre métrica, valor)
            # Structure: (Team, [GoalsScored, GoalsConceded, RedCards, YellowCards, Wins])
            yield home, [h_goals, a_goals, h_red, h_yellow, h_win]
            yield away, [a_goals, h_goals, a_red, a_yellow, a_win]
            
        except (ValueError, IndexError):
            pass

    def reducer_aggregate_stats(self, team, stats_list):
        total_gs = 0
        total_gc = 0
        total_red = 0
        total_yel = 0
        total_wins = 0
        
        for s in stats_list:
            total_gs += s[0]
            total_gc += s[1]
            total_red += s[2]
            total_yel += s[3]
            total_wins += s[4]
            
        yield team, {
            "Goles_Favor": total_gs,
            "Goles_Contra": total_gc,
            "Rojas": total_red,
            "Amarillas": total_yel,
            "Victorias": total_wins
        }

if __name__ == '__main__':
    MRAdvancedLaLiga.run()
