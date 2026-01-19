import json
import sys

def parse_and_rank(filename):
    data = []
    try:
        # PowerShell redirection often creates UTF-16 files
        with open(filename, 'r', encoding='utf-16') as f:
            lines = f.readlines()
    except UnicodeError:
        # Fallback to UTF-8 if it wasn't UTF-16
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
    for line in lines:
            # MrJob output is: "Key"\tValue_JSON
            try:
                parts = line.split('\t')
                team = parts[0].strip('"')
                stats = json.loads(parts[1])
                stats['Team'] = team
                data.append(stats)
            except:
                continue

    print("\n--- TOP 5: EQUIPOS CON MAS TARJETAS ROJAS (Juego sucio) ---")
    sorted_red = sorted(data, key=lambda x: x['Rojas'], reverse=True)[:5]
    for i, d in enumerate(sorted_red, 1):
        print(f"{i}. {d['Team']}: {d['Rojas']} rojas")

    print("\n--- TOP 5: EQUIPOS CON MAS GOLES (Poder ofensivo) ---")
    sorted_goals = sorted(data, key=lambda x: x['Goles_Favor'], reverse=True)[:5]
    for i, d in enumerate(sorted_goals, 1):
        print(f"{i}. {d['Team']}: {d['Goles_Favor']} goles")

    print("\n--- TOP 5: EQUIPOS CON MAS GOLES EN CONTRA (Peor defensa) ---")
    sorted_conceded = sorted(data, key=lambda x: x['Goles_Contra'], reverse=True)[:5]
    for i, d in enumerate(sorted_conceded, 1):
        print(f"{i}. {d['Team']}: {d['Goles_Contra']} recibidos")

    print("\n--- TOP 5: EQUIPOS CON MAS VICTORIAS (Dominio total) ---")
    sorted_wins = sorted(data, key=lambda x: x['Victorias'], reverse=True)[:5]
    for i, d in enumerate(sorted_wins, 1):
        print(f"{i}. {d['Team']}: {d['Victorias']} victorias")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        parse_and_rank(sys.argv[1])
    else:
        print("Usage: python analyze_results.py <results_file>")
