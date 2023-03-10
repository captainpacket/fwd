# Post City Data to API

This script reads in a CSV file containing city data for Washington state, filters the data to include only Washington cities, and posts the data to an API endpoint.

## Requirements

To run this script, you will need the following packages:

- pandas
- requests

You can install these packages using pip:

pip install pandas requests

## Usage

To use this script, follow these steps:

1. Create a CSV file containing city data, in the format "city","city_ascii","city_alt","lat","lng","country","iso2","iso3","admin_name","admin_name_ascii","admin_code","admin_type","capital","density","population","population_proper","ranking","timezone","same_name","id".
2. Filter the data to include only Washington state cities.
3. Replace the `your_api_host` and `your_network_id` variables in the script with the appropriate values for your API endpoint.
4. Run the script using the following command:

python post_city_data.py

## Command Line Arguments

The script accepts the following command line arguments:

- `--host`: The API host (required)
- `--network-id`: The network ID (required)
- `--username`: The API username (required)
- `--password`: The API password (required)

To specify command line arguments, use the following format:

python post_city_data.py --host example.com --network-id 12345 --username myusername --password mypassword

## Washington Cities CSV File

To use this script, you will also need the `washington_cities.csv` file, which contains city data for Washington state. This file is included in this repository.

To download the file, either clone this repository using Git, or download the file directly from the GitHub website.

To clone the repository using Git, run the following command in your terminal:

git clone https://github.com/fracticated/fwd.git

This will create a local copy of the repository on your computer, including the `washington_cities.csv` file.

Alternatively, you can download the file directly from the GitHub website by following these steps:

1. Navigate to the repository on the GitHub website.
2. Click on the `washington_cities.csv` file in the file list.
3. Click the "Download" button to download the file.

Once you have downloaded the `washington_cities.csv` file, place it in the same directory as the `post_city_data.py` script. Then, you can run the script using the instructions provided in the "Usage" section above.

## License

This script is released under the MIT License. See the LICENSE file for details.



