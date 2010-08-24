# This is a collection of Python code snippets I use to transform the data


# Takes the raw list of company information, and turns it into a CSV file
import os, sys, csv
try:
    import simplejson as json
except ImportError:
    import json

def getSafe(input):
    if input is None:
        return ''
    else:
        try:
            result = input.encode('ascii', 'replace')
        except:
            result = input
        return result

input = open('companydata.txt', 'rb')
writer = csv.writer(open('companydata.csv', 'wb'))

writer.writerow(['name', 'founded_year', 'country_code', 'state_code', 'zip_code', 'city', 'address1', 'address2', 'raised_amount'])

position = 1
for line in input.readlines():
    try:
        data = json.loads(line)
    except:
        continue
    if not 'name' in data:
        continue
    
    name = getSafe(data['name'])
    founded_year = getSafe(data['founded_year'])
    offices = data['offices']
    if len(offices)<1:
        continue
    
    # Assume the head office is the first one listed
    office = offices[0]
    country_code = getSafe(office['country_code'])
    state_code = getSafe(office['state_code'])
    zip_code = getSafe(office['zip_code'])
    city = getSafe(office['city'])
    address1 = getSafe(office['address1'])
    address2 = getSafe(office['address2'])
    
    funding_rounds = data['funding_rounds']
    amount_raised = 0
    for funding_round in funding_rounds:
        if funding_round['raised_currency_code'] != 'USD':
            continue
        if funding_round['raised_amount'] is None:
            continue
        amount_raised += funding_round['raised_amount']
        
    writer.writerow([name, founded_year, country_code, state_code, zip_code, city, address1, address2, amount_raised])



# Pulls the Census zip code population data into a dictionary called zip_info
import os, sys, csv

input = open('zcta5.txt')

zip_info = {}
for line in input.readlines():
    state_code = line[0:2]
    zip_code = line[2:7]
    population = line[66:75]
    lat = line[136:146]
    lon = line[146:156]
    zip_info[zip_code] = { 'state_code': state_code, 'population': population, 'lat': lat, 'lon': lon }



# Reads in the company data and outputs the company/population ratio and location for all
# recognized zip codes
import os, sys, csv

reader = csv.reader(open('companydata.csv', 'rb'))

zip_counts = {}

line_index = 0
for row in reader:
    line_index += 1
    if line_index == 1:
        continue
    
    name = row[0]
    country_code = row[2]
    if country_code != 'USA': # USA! USA!
        continue
    
    state_code = row[3]
    zip_code = row[4]
    if not zip_code in zip_info:
        continue
    
    try:
        amount_raised = float(row[8])
    except:
        print row[8]
        amount_raised = 0
    
    if not zip_code in zip_counts:
        info = zip_info[zip_code]
        population = int(info['population'])
        lat = float(info['lat'])
        lon = float(info['lon'])
        zip_counts[zip_code] = { 'lat': lat, 'lon': lon, 'population': population, 'companies': [], 'amount_raised': 0 }
    
    zip_counts[zip_code]['companies'].append(name)
    zip_counts[zip_code]['amount_raised'] += amount_raised



# Takes the raw list of company information, and turns it into a CSV file
import os, sys, csv, string
try:
    import simplejson as json
except ImportError:
    import json

writer = csv.writer(open('zips_by_numbers.csv', 'wb'))

writer.writerow(['lat', 'lon', 'value', 'tooltip'])

for zip_code, info in zip_counts.items():
    companies = info['companies']
    company_count = len(companies)
    tooltip = str(zip_code)+' - '
    tooltip += str(company_count)
    if company_count>1:
        tooltip += ' companies - '
    else:
        tooltip += ' company - '
    if company_count>5:
        tooltip += ', '.join(companies[:5])+', ...'
    else:
        tooltip += ', '.join(companies)
    population = info['population']
    if population < 250: # Exclude zip codes with almost nobody in them
        continue
    lat = info['lat']
    lon = info['lon']
    value = float(company_count)/population
    tooltip += ' - '+str(value)+' per person'
    writer.writerow([lat, lon, value, tooltip])



# Takes the raw list of company information, and turns it into a CSV file
import os, sys, csv, string, locale
try:
    import simplejson as json
except ImportError:
    import json

# http://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators-in-python-2-x
def intWithCommas(x):
    if x < 0:
        return '-' + intWithCommas(-x)
    result = ''
    while x >= 1000:
        x, r = divmod(x, 1000)
        result = ",%03d%s" % (r, result)
    return "%d%s" % (x, result)

writer = csv.writer(open('zips_by_amount.csv', 'wb'))

writer.writerow(['lat', 'lon', 'value', 'tooltip'])

for zip_code, info in zip_counts.items():
    companies = info['companies']
    amount_raised = info['amount_raised']
    if amount_raised < 1:
        continue
    company_count = len(companies)
    tooltip = str(zip_code)+' - $'
    tooltip += intWithCommas(amount_raised)
    if company_count>1:
        tooltip += ' - '
    else:
        tooltip += ' - '
    if company_count>5:
        tooltip += ', '.join(companies[:5])+', ...'
    else:
        tooltip += ', '.join(companies)
    population = info['population']
    if population < 250: # Exclude zip codes with almost nobody in them
        continue
    lat = info['lat']
    lon = info['lon']
    value = amount_raised/population
    tooltip += ' - $'+intWithCommas(value)+' per person'
    writer.writerow([lat, lon, value, tooltip])



