import csv
from collections import defaultdict
from functions import analysperiod
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


    




#start, slut = analysperiod("network_incidents.csv")
#print(f"Analysperiod: {start} till {slut}")



# Write to a CSV file
# w = write, utf-8 good encoding for åäö etc, 
# newline = nothing/empty string since the csv-library handles new lines 

#with open('salary-stats.csv', 'w', encoding='utf-8', newline='') as f:

    #writer = csv.DictWriter(f, fieldnames = ['Summering', 'Värde'])

    #writer.writeheader()

    #writer.writerows(summary)