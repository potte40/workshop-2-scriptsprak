import csv
from collections import defaultdict
from functions import analysperiod
from functions import swedishNumberStringsToFloat
from functions import safe_float
with open('network_incidents.csv', encoding='utf-8') as f:

    incidents = list(csv.DictReader(f))


# Dictionary för att räkna antal incidents per severity
severity_count = defaultdict(int)

# Loop över varje incident
for inc in incidents:
    print(inc["site"], inc["week_number"])
    severity = inc.get("severity", "").strip().lower()
    if severity:
        severity_count[severity] += 1

for sev in ["critical", "high", "medium", "low"]:
    print(sev.capitalize() + " - " + str(severity_count.get(sev, 0)))

high_impact_incidents = [inc for inc in incidents if swedishNumberStringsToFloat(inc.get("affected_users", 0)) > 100]
for inc in high_impact_incidents:
    print(f"Site: {inc['site']}, Affected Users: {inc['affected_users']}, Severity: {inc['severity']}")

### Topp 5 dyraste incidenterna ###
for inc in incidents:
    inc["cost_sek"] = swedishNumberStringsToFloat(inc.get("cost_sek", "0"))

# Sortera efter kostnad, högst först
dyraste = sorted(incidents, key=lambda x: x["cost_sek"], reverse=True)[:5]

# Skriv ut
for inc in dyraste:
    print(    
        f"Site: {inc.get('site', 'okänd')}, "
        f"Kostnad: {inc.get('cost_sek', 'saknas')}, "
    )


# Beräkna total kostnad
total_cost = sum(float(inc.get("cost_sek", 0)) for inc in incidents)
# Skriv ut
print(f"Totalkostnad för alla incidenter: {total_cost:.2f} kr")


# Dictionary för att lagra total tid och antal per severity
severity_time = defaultdict(lambda: {"sum": 0.0, "count": 0})

# Loop över incidenterna
for inc in incidents:
    severity = inc.get("severity", "").strip().lower()
    resolution = swedishNumberStringsToFloat(inc.get("resolution_minutes", "0"))
    if severity and resolution > 0:
        severity_time[severity]["sum"] += resolution
        severity_time[severity]["count"] += 1

# Beräkna och skriv ut genomsnitt
print("\nGenomsnittlig resolution time per severity:")
for sev in ["critical", "high", "medium", "low"]:
    data = severity_time.get(sev, {"sum": 0, "count": 0})
    if data["count"] > 0:
        avg = data["sum"] / data["count"]
        print(f"{sev.capitalize():<10}: {avg:.1f} minuter i snitt ({data["count"]} incidenter)")
    else:
        print(f"{sev.capitalize():<10}: ingen data")


# Identifiera kolumner dynamiskt
cost_column = next((k for k in incidents[0].keys() if "cost" in k.lower()), "cost_sek")
resolution_column = next((k for k in incidents[0].keys() if "resolution" in k.lower()), None)
site_column = next((k for k in incidents[0].keys() if "site" in k.lower()), None)

# Initiera struktur per site
site_stats = defaultdict(lambda: {"count": 0, "total_cost": 0.0, "total_resolution": 0.0, "resolution_count": 0})

for inc in incidents:
    site = inc.get(site_column, "okänd")
    
    # Räknar antal incidents
    site_stats[site]["count"] += 1

    # Lägg till kostnad
    cost = float(inc.get(cost_column, "0"))
    site_stats[site]["total_cost"] += cost

    # Lägg till resolution
    if resolution_column:
        resolution = swedishNumberStringsToFloat(inc.get(resolution_column, "0"))
        if resolution > 0:
            site_stats[site]["total_resolution"] += resolution
            site_stats[site]["resolution_count"] += 1

# Skriv ut resultat
print(f"{'Site':<20}{'Incidents':<10}{'Total Kostnad':<20}{'Genomsnittlig Resolution (min)'}")
print("-"*70)
for site, stats in site_stats.items():
    avg_resolution = (stats["total_resolution"] / stats["resolution_count"]) if stats["resolution_count"] > 0 else 0
    print(f"{site:<20}{stats['count']:<10}{stats['total_cost']:<20.2f}{avg_resolution:.2f}")


category_stats = defaultdict(lambda: {"sum_impact": 0.0, "count": 0})

for inc in incidents:
    category = inc.get("category", "okänd").strip()
    impact = swedishNumberStringsToFloat(inc.get("impact_score", "0"))
    
    if category and impact > 0:
        category_stats[category]["sum_impact"] += impact
        category_stats[category]["count"] += 1

# Skriv ut resultat
print(f"{'Kategori':<20}{'Antal Incidents':<15}{'Genomsnittlig Impact'}")
print("-" * 50)
for cat, stats in category_stats.items():
    avg_impact = stats["sum_impact"] / stats["count"] if stats["count"] > 0 else 0
    print(f"{cat:<20}{stats['count']:<15}{avg_impact:.2f}")


# Skapa en lista av dictionaries för varje site
site_summary = []
for site, stats in site_stats.items():
    avg_resolution = (stats["total_resolution"] / stats["resolution_count"]) if stats["resolution_count"] > 0 else 0
    site_summary.append({
        "Site": site,
        "Antal Incidents": stats["count"],
        "Total Kostnad": f"{stats['total_cost']:.2f}",
        "Genomsnittlig Resolution (min)": f"{avg_resolution:.2f}"
    })
    
# Skriv incidents_by_site till CSV
with open('incidents_by_site.csv', 'w', encoding='utf-8', newline='') as f:
    fieldnames = ["Site", "Antal Incidents", "Total Kostnad", "Genomsnittlig Resolution (min)"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(site_summary)

print("CSV-fil 'incidents_by_site.csv' skapad!")

#start, slut = analysperiod("network_incidents.csv")
#print(f"Analysperiod: {start} till {slut}")



# Write to a CSV file
# w = write, utf-8 good encoding for åäö etc, 
# newline = nothing/empty string since the csv-library handles new lines 

#with open('salary-stats.csv', 'w', encoding='utf-8', newline='') as f:

    #writer = csv.DictWriter(f, fieldnames = ['Summering', 'Värde'])

    #writer.writeheader()

    #writer.writerows(summary)