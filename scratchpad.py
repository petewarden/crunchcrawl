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

import sys, string, json

input = open('vcdata.txt', 'rb')

vclist = []

for line in input.readlines():
    try:
        current_parts = string.split(line, "\t", 1)
        if len(current_parts) < 2:
            continue
            
        current_key = current_parts[0]
        current_data = json.loads(current_parts[1])
        
        investments = current_data['investments']
        
        total_investment_count = len(investments)
        total_investment_amount = 0
        for investment in investments:
            total_investment_amount += investment['investment_amount']
            
        current_data['permalink'] = current_key
        current_data['total_investment_count'] = total_investment_count
        current_data['total_investment_amount'] = total_investment_amount
        
        vclist.append(current_data)
        
    except:
        raise

vc_by_count = sorted(vclist, key=lambda vc: vc['total_investment_count'])
vc_by_count.reverse()
vc_by_amount = sorted(vclist, key=lambda vc: vc['total_investment_amount'])
vc_by_amount.reverse()

wanted_vcs = {
    'union-square-ventures': True,
    'foundry-group': True
}

index = 0
for vc in vc_by_count:
    if index>=100:
        break
    index += 1
    wanted_vcs[vc['permalink']] = True

index = 0
for vc in vc_by_amount:
    if index>=100:
        break
    index += 1
    wanted_vcs[vc['permalink']] = True

import csv

for vc in vclist:
    permalink = vc['permalink']
    if permalink not in wanted_vcs:
        continue
        
    investments = vc['investments']
    locations = {}
    for investment in investments:
        city = string.capwords(investment['city'].strip())
        if city == '':
            continue
        state_code = string.capwords(investment['state_code'].strip())
        country_code = string.upper(investment['country_code'].strip())
        investment_amount = investment['investment_amount']
        company_name = investment['company_name']
        key = city+', '+state_code+', '+country_code
        if key not in locations:
            locations[key] = { 'amount': 0, 'companies': {}, 'city': city }
        locations[key]['amount'] += investment_amount
        locations[key]['companies'][company_name] = True
    writer = csv.writer(open('mapfiles/'+permalink+'.csv', 'wb'))
    writer.writerow(['location', 'value', 'tooltip'])
    for location, info in locations.items():
        amount = info['amount']
        value = round(amount/1000000, 1)
        city = info['city']
        tooltip = city+' - '+str(value)+'m - '
        tooltip += ', '.join(info['companies'].keys())
        writer.writerow([location, value, tooltip])



import sys, json, urllib, os

default_settings = {"general":{"gradient_start_color":"#00f500","gradient_mid_color":"#00b800","gradient_end_color":"#006b00","author_name":"Pete Warden","author_url":"petewarden.typepad.com\/","key_description":"Investment amount (millions)","gradient_with_alpha":["#9300f500","#9300b800","#93006b00"],"details_value":0.42},"component":{"gradient_value_min":"0.0","gradient_value_max":"50","point_blob_radius":31.36,"title_text":"NA","point_drawing_shape":"circle","circle_line_color":0,"circle_line_alpha":1,"circle_line_thickness":1,"is_point_blob_radius_in_pixels":True},"way":{}}

for vc in vclist:
    permalink = vc['permalink']
    if permalink not in wanted_vcs:
        continue
    csv_file = permalink+'.csv'
    csv_path = 'mapfiles/'+csv_file
    override_settings = default_settings
    override_settings['component']['title_text'] = vc['name']
    override_settings_string = urllib.quote(json.dumps(override_settings))
    command_line = 'curl --data-binary @'+csv_path
    command_line += ' --silent'
    command_line += ' "http://www.openheatmap.com/uploadcsv.php?qqfile='+csv_file
    command_line += '&disable_base64'
    command_line += '&override_settings='+override_settings_string
    command_line += '"'
    command_line += ' > /tmp/foo.json'
    error = os.system(command_line)
    result = json.loads(open('/tmp/foo.json').read())
    print '<tr><td><a href="http://www.openheatmap.comview.html?map='+result['output_id']+'">'+vc['name']+'</a></td><td><a href="http://www.crunchbase.com/financial-organization/'+vc['permalink']+'">'+str(vc['total_investment_count'])+' investments totalling '+str(round(vc['total_investment_amount']/1000000, 1))+'m</a></td></tr>'


