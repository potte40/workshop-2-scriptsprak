from datetime import date, timedelta
import csv


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