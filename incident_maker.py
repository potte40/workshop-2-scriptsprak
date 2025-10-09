import csv
from collections import defaultdict
from functions import analysperiod
with open('network_incidents.csv', encoding='utf-8') as f:

    incidents = list(csv.DictReader(f))


severity_count = defaultdict(int)


for inc in incidents:
    print (inc["site"], inc["week_number"])



#start, slut = analysperiod("network_incidents.csv")
#print(f"Analysperiod: {start} till {slut}")



# Write to a CSV file
# w = write, utf-8 good encoding for åäö etc, 
# newline = nothing/empty string since the csv-library handles new lines 

#with open('salary-stats.csv', 'w', encoding='utf-8', newline='') as f:

    #writer = csv.DictWriter(f, fieldnames = ['Summering', 'Värde'])

    #writer.writeheader()

    #writer.writerows(summary)