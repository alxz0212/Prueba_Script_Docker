import json

def get_stats():
    data = []
    # Try reading with utf-8 first (standard), then utf-16 (powershell legacy)
    try:
        lines = open('advanced_results.txt', 'r', encoding='utf-8').readlines()
    except UnicodeDecodeError:
        lines = open('advanced_results.txt', 'r', encoding='utf-16').readlines()

    for line in lines:
        try:
            if not line.strip(): continue
            parts = line.split('\t')
            if len(parts) < 2: continue
            
            # parts[1] is the JSON value
            stats = json.loads(parts[1])
            # parts[0] is the key (Team Name) which might be quoted
            stats['Team'] = parts[0].strip('"')
            data.append(stats)
        except Exception as e:
            continue

    if not data:
        print("NO DATA FOUND")
        return

    print("ROJAS:")
    for d in sorted(data, key=lambda x:x['Rojas'], reverse=True)[:5]:
        print(f"{d['Team']}: {d['Rojas']}")
        
    print("\nGOLES:")
    for d in sorted(data, key=lambda x:x['Goles_Favor'], reverse=True)[:5]:
        print(f"{d['Team']}: {d['Goles_Favor']}")

    print("\nDEFENSA (Goles Recibidos):")
    for d in sorted(data, key=lambda x:x['Goles_Contra'], reverse=True)[:5]:
        print(f"{d['Team']}: {d['Goles_Contra']}")

    print("\nVICTORIAS:")
    for d in sorted(data, key=lambda x:x['Victorias'], reverse=True)[:5]:
        print(f"{d['Team']}: {d['Victorias']}")

if __name__ == "__main__":
    get_stats()
