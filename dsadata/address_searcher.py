import csv
import pprint
import requests
import sys

PELIAS_URL = "http://localhost:4000"

def search_address(address):
    res = requests.get(PELIAS_URL + "/v1/search", params={"text":address})
    json_data = res.json()
    features = json_data['features']
    if not len(features) or len(features) == 0:
        return ''
    else:
        coords = features[0]['geometry']['coordinates']
        return coords

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: address_searcher.py <filename>')
        sys.exit(1)
    (_, file_name) = sys.argv
    with open(file_name, newline='') as file:
        data = []
        reader = csv.reader(file, delimiter=',', quotechar='"')
        for line in reader:
            data.append(line)
    # first line is column header
    column_names = data[0]
    column_names.append("Latitude")
    column_names.append("Longitude")
    results = []
    results.append(column_names)
    data = data[1:]
    state_counts = {} 
    state_amounts = {}
    for line in data:
        address_data = line[7:12]
        amount = float(line[-3])
        state = address_data[3]
        if len(state) > 2 or len(state) <= 0:
            # TODO: State data not found here, fix these cases
            print("THIS SHOULDN'T HAPPEN")
            sys.exit()
            continue
        if state == 'MP':
            # TODO: this is a singular typo, fix in data
            state = 'MO'
        full_address = ' '.join(address_data)
        if state == 'MO':
            res = search_address(full_address)
            if len(res) == 2:
                lat, lon = res
                line.append(lat)
                line.append(lon)
            line = [str(x) for x in line]
            results.append(line)
    with open('results.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"')
        for line in results:
            writer.writerow(line)
