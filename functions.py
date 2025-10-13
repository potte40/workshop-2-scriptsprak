from datetime import date, timedelta
import csv
    
def safe_float(value):
    
    try:
        s = str(value).replace(" ", "").replace(",", ".")
        return float(s)
    except (ValueError, TypeError):
        return 0.0

### Analysperiod ###
def veckointervall(år, vecka):
    start = date.fromisocalendar(år, vecka, 1)
    slut = start + timedelta(days=6)
    return start, slut

def analysperiod(network_incidents, kolumn_namn="week_number", fallback_år=None):

    if fallback_år is None:
        fallback_år = date.today().year - 1

    startdatum = []
    slutdatum = []

    with open("network_incidents.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for rad in reader:
            vecka_str = rad.get("week_number", '').strip()
            if not vecka_str:
                continue
            try:
                if '-' in vecka_str:
                    år, vecka = map(int, vecka_str.split('-'))
                else:
                    år = fallback_år
                    vecka = int(vecka_str)
                start, slut = veckointervall(år, vecka)
                startdatum.append(start)
                slutdatum.append(slut)
            except ValueError:
                continue

    if not startdatum:
        return None, None

    return min(startdatum).isoformat(), max(slutdatum).isoformat()




### Felhantering för trasig data och rapportera för datakvalitetsproblem

def check_data_quality(incidents):
    # Går igenom en lista av incidenter och identifierar datakvalitetsproblem.
    # Returnerar en lista med felmeddelanden.
    issues = []
    
    for i, inc in enumerate(incidents, start=1):
        site = inc.get("site")
        device = inc.get("device_hostname")
        severity = inc.get("severity")
        cost = inc.get("cost_sek")
        resolution = inc.get("resolution_minutes")
        
        # Saknade obligatoriska fält
        if not site or not device:
            issues.append(f"Rad {i}: Saknas site eller device_hostname")
        
        # Ogiltig severity
        if severity and severity.strip().lower() not in ["critical", "high", "medium", "low"]:
            issues.append(f"Rad {i}: Ogiltig severity '{severity}'")
        
        # Numeriska fält
        try:
            safe_float(cost)
        except Exception:
            issues.append(f"Rad {i}: Kostnad '{cost}' kan inte omvandlas till float")
        
        try:
            safe_float(resolution)
        except Exception:
            issues.append(f"Rad {i}: Resolution '{resolution}' kan inte omvandlas till float")
    
    return issues