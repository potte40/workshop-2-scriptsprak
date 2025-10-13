import csv
from collections import defaultdict
from datetime import datetime
from functions import analysperiod, safe_float, check_data_quality
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

high_impact_incidents = [inc for inc in incidents if safe_float(inc.get("affected_users", 0)) > 100]
for inc in high_impact_incidents:
    print(f"Site: {inc['site']}, Affected Users: {inc['affected_users']}, Severity: {inc['severity']}")

### Topp 5 dyraste incidenterna ###
for inc in incidents:
    inc["cost_sek"] = safe_float(inc.get("cost_sek", "0"))

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
    resolution = safe_float(inc.get("resolution_minutes", "0"))
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
        resolution = safe_float(inc.get(resolution_column, "0"))
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
    impact = safe_float(inc.get("impact_score", "0"))
    
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


### problem_devices.csv

# Skapa statistik per enhet
device_stats = defaultdict(lambda: {"count": 0, "total_cost": 0.0})

for inc in incidents:
    device = inc.get("device_hostname", "okänd").strip()
    cost = safe_float(inc.get("cost_sek", 0))
    
    device_stats[device]["count"] += 1
    device_stats[device]["total_cost"] += cost

# Skapa lista för CSV
device_summary = [
    {
        "Device": dev,
        "Antal Incidents": stats["count"],
        "Total Kostnad": f"{stats['total_cost']:.2f}"
    }
    for dev, stats in device_stats.items()
]

# Sortera devices efter antal incidents och sedan total kostnad
device_summary.sort(key=lambda x: (x["Antal Incidents"], safe_float(x["Total Kostnad"])), reverse=True)

# Skriv till CSV
with open('problem_devices.csv', 'w', encoding='utf-8', newline='') as f:
    fieldnames = ["Device", "Antal Incidents", "Total Kostnad"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(device_summary)

print("CSV-fil 'problem_devices.csv' skapad!")


### cost_analysis.csv

# Dictionary för veckovis statistik
weekly_stats = defaultdict(lambda: {"total_cost": 0.0, "total_impact": 0.0, "count": 0})

for inc in incidents:
    week = inc.get("week_number", "okänd")
    cost = safe_float(inc.get("cost_sek", 0))
    impact = safe_float(inc.get("impact_score", 0))
    
    weekly_stats[week]["total_cost"] += cost
    weekly_stats[week]["total_impact"] += impact
    weekly_stats[week]["count"] += 1

# Skapa lista för CSV
weekly_summary = []
for week, stats in sorted(weekly_stats.items()):
    avg_impact = stats["total_impact"] / stats["count"] if stats["count"] > 0 else 0
    weekly_summary.append({
        "Week": week,
        "Total Kostnad": f"{stats['total_cost']:.2f}",
        "Genomsnittlig Impact": f"{avg_impact:.2f}",
        "Antal Incidents": stats["count"]
    })

# Skriv till CSV
with open('cost_analysis.csv', 'w', encoding='utf-8', newline='') as f:
    fieldnames = ["Week", "Antal Incidents", "Total Kostnad", "Genomsnittlig Impact"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(weekly_summary)

print("CSV-fil 'cost_analysis.csv' skapad!")



### Textrapport ###

# Sammanställning
total_incidents = len(incidents)
total_cost = sum(safe_float(inc.get("cost_sek", 0)) for inc in incidents)
dyraste = max(incidents, key=lambda x: safe_float(x.get("cost_sek", 0)))

# Analysperiod
start, slut = analysperiod("network_incidents.csv")
# Konverterat till månad och år
månad_år = datetime.strptime(start, "%Y-%m-%d").strftime("%B %Y").upper()


# Sammanställning per site och severity
site_stats = defaultdict(lambda: {"critical": 0, "high": 0, "medium": 0, "low": 0})
severity_stats = defaultdict(lambda: {"count": 0, "sum_cost": 0.0, "sum_resolution": 0.0})

for inc in incidents:
    site = inc.get("site", "okänd").strip()
    sev = inc.get("severity", "").strip().lower()
    cost = safe_float(inc.get("cost_sek", "0"))
    resolution = safe_float(inc.get("resolution_minutes", "0"))

    if sev:
        site_stats[site][sev] += 1
        severity_stats[sev]["count"] += 1
        severity_stats[sev]["sum_cost"] += cost
        severity_stats[sev]["sum_resolution"] += resolution

#Identifiera sites utan critical incidents
sites_no_critical = [s for s, stats in site_stats.items() if stats["critical"] == 0]

### EXECUTIVE SUMMARY ###
dyraste_cost = safe_float(dyraste.get("cost_sek", 0))
dyraste_text = f"{dyraste_cost:,.2f} SEK ({dyraste['site']} - {dyraste.get('category', 'okänd')}) - {dyraste.get('device_hostname', 'okänd enhet')}"

summary_lines = []
summary_lines.append("EXECUTIVE SUMMARY\n-----------------")

# Mest kritiska site
kritisk_site = max(site_stats.items(), key=lambda kv: kv[1]["critical"])[0]
kritisk_count = site_stats[kritisk_site]["critical"]
if kritisk_count > 0:
    summary_lines.append(f"⚠ KRITISKT: {kritisk_site} har {kritisk_count} critical incidents")

summary_lines.append(f"⚠ KOSTNAD: Dyraste incident: {dyraste_text}")
summary_lines.append(f"⚠ Totalt {total_incidents} incidenter rapporterade under perioden")
if high_impact_incidents:
    summary_lines.append(f"⚠ {len(high_impact_incidents)} incidenter påverkar mer än 100 användare")

# Positiv del
if sites_no_critical:
    summary_lines.append("✓ POSITIVT: Inga critical incidents på följande sites:")
    for s in sites_no_critical:
        summary_lines.append(f"   - {s}")

# INCIDENTS PER SEVERITY
severity_section = ["\nINCIDENTS PER SEVERITY\n----------------------"]
for sev in ["critical", "high", "medium", "low"]:
    data = severity_stats[sev]
    if data["count"] > 0:
        avg_res = data["sum_resolution"] / data["count"]
        avg_cost = data["sum_cost"] / data["count"]
        perc = (data["count"] / total_incidents) * 100
        severity_section.append(
            f"{sev.capitalize():<10}: {data['count']:>3} st ({perc:>4.1f}%) - "
            f"Genomsnitt: {avg_res:.1f} resolution min, {avg_cost:,.0f} SEK/incident"
        )
    else:
        severity_section.append(f"{sev.capitalize():<10}: inga incidenter")





# Bygger rapporten
report_lines = []
report_lines.append("=" * 80)
report_lines.append(" " * 19 + "INCIDENT ANALYSIS - " + månad_år)
report_lines.append("=" * 80)
report_lines.append(f"\nAnalysperiod: {start} till {slut}")
report_lines.append(f"Total incidents: {total_incidents} st")
report_lines.append(f"Total kostnad: {total_cost:,.2f} SEK\n")
report_lines.extend(summary_lines)
report_lines.append("")
report_lines.extend(severity_section)


# Räkna antal incidents och total kostnad per enhet
device_stats = defaultdict(lambda: {"count": 0, "total_cost": 0.0})

for inc in incidents:
    device = inc.get("device_hostname", "okänd").strip()
    cost = safe_float(inc.get("cost_sek", 0))
    device_stats[device]["count"] += 1
    device_stats[device]["total_cost"] += cost

# Identifiera enheter med problem med fler än 2 incidents eller hög kostnad
problem_devices = []
for device, stats in device_stats.items():
    if stats["count"] > 2 or stats["total_cost"] > 50000:
        problem_devices.append({
            "device": device,
            "incidents": stats["count"],
            "total_cost": stats["total_cost"],
            "suggested_action": "Kontrollera hårdvara/firmware, utvärdera byte av hårdvara"
        })

# Sortera problem devices efter antal incidents eller kostnad
problem_devices_sorted = sorted(problem_devices, key=lambda x: (x["incidents"], x["total_cost"]), reverse=True)

# Lägg till i report_lines
report_lines.append("\nPROBLEM DEVICES\n----------------")
if problem_devices_sorted:
    for d in problem_devices_sorted:
        line = (
            f"{d['device']}: {d['incidents']} incidents, "
            f"Total kostnad: {d['total_cost']:,.2f} SEK, "
            f"Föreslagen åtgärd: {d['suggested_action']}"
        )
        report_lines.append(line)
else:
    report_lines.append("Inga återkommande problem identifierade.")


# Felhantering för trasig data och rapportera för datakvalitetsproblem

data_quality_issues = check_data_quality(incidents)

# Lägg till i rapporten
report_lines.append("\nDATA QUALITY ISSUES\n-------------------")
if data_quality_issues:
    for issue in data_quality_issues:
        report_lines.append(f"⚠ {issue}")
else:
    report_lines.append("Inga datakvalitetsproblem identifierade.")

# Skriv till terminalen
print("\n".join(report_lines))

# Skriv till textdokument
with open("incident_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print("\nTextfil 'incident_report.txt' skapad!")




