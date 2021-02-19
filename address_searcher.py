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
    with open(file_name, 'r') as file:
        data = file.readlines()
    # first line is column header
    column_names = data[0].replace('\n', '').split(',')
    results = []
    results.append(data[0] + "Latitude,Longitude")
    data = data[1:]
    state_counts = {} 
    state_amounts = {}
    for line in data:
        split_line = line.split(',')
        address_data = split_line[7:12]
        amount = float(split_line[-3])
        state = address_data[3]
        if len(state) > 2:
            state = address_data[4]
            if len(state) > 2:
                # only 4 cases of this, plus one super jacked up case
                state = split_line[2]
                if len(state) > 2:
                    # TODO: fix the lines that causes this case to be executed at all
                    continue
        elif len(state) > 2 or len(state) <= 0:
            # TODO: State data not found here, fix these cases
            continue
        if state == 'MP':
            # TODO: this is a singular typo, fix in data
            state = 'MO'
        full_address = ' '.join(address_data)
        if state == 'MO':
            res = search_address(full_address)
            if len(res) == 2:
                lat, lon = res
                results.append("{},{},{}".format(line, lat, lon))
            results.append("{},,".format(line))
    with open('results.csv', 'w') as file:
        file.write('\n'.join(results))
