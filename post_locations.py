import argparse
import pandas as pd
import requests

# create an argparse ArgumentParser object
parser = argparse.ArgumentParser(description="Post city data to an API")

# add command line arguments for the API host, network ID, username, and password
parser.add_argument("--host", type=str, required=True, help="The Forward Networks API host")
parser.add_argument("--network-id", type=int, required=True, help="The Forward Networks Network ID")
parser.add_argument("--username", type=str, required=True, help="The Forward Networks API username")
parser.add_argument("--password", type=str, required=True, help="The Forward Networks API password")

# parse the command line arguments
args = parser.parse_args()

# read in the CSV file containing only Washington state cities
df = pd.read_csv('washington_cities.csv', dtype={'admin_code': str})

# construct the API endpoint URL
api_url = f"https://{args.host}/api/networks/{args.network_id}/locations"

# loop over rows in the filtered dataframe and post to the API
for index, row in df.iterrows():
    # construct the JSON payload
    payload = {
        "name": row['city_ascii'],
        "lat": row['lat'],
        "lng": row['lng']
    }
    # make the API request with basic authentication
    response = requests.post(api_url, json=payload, auth=(args.username, args.password), verify=False)
    # check the response status code
    if response.status_code == 200:
        print(f"Posted data for {row['city_ascii']} successfully")
    else:
        print(f"Error posting data for {row['city_ascii']}: {response.text}")

