from datetime import date, timedelta
import csv

# Declare a function that convert Swedish numbers

# with ' ' as thousand separators and ',' 

# as decimal separators to float

# - DECLARE A FUNCTION BEFORE CALLING IT

# Declare a function that convert Swedish numbers

# with ' ' as thousand separators and ',' 

# as decimal separators to float

# - DECLARE A FUNCTION BEFORE CALLING IT

def swedishNumberStringsToFloat(string):

    # try - try to do something that we know

    # might give us a runtime error / "crash the program"

    try:

        return float(string.replace(' ','').replace(',','.'))

    # handle exceptions - when what we tried didn't work

    except:

        # return 0 if we can't convert to a number

        return 0
    


def safe_float(value):
    """Konverterar svenska siffror t.ex. '1 234,5' -> 1234.5"""
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