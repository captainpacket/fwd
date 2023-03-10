# Post City Data to API

This script reads in a CSV file containing city data for Washington state, and posts the data to an API endpoint.

## Requirements

To run this script, you will need the following packages:

- pandas
- requests

You can install these packages using pip:

`pip install pandas requests`

## Usage

`usage: post_locations.py [-h] --host HOST --network-id NETWORK_ID --username USERNAME --password PASSWORD`

## Command Line Arguments

The script accepts the following command line arguments:

- `--host`: The Forward Networks API host (required)
- `--network-id`: The Forward Networks network ID (required)
- `--username`: The Forward Networks API username (required)
- `--password`: The Forward Networks API password (required)

To specify command line arguments, use the following format:

`python post_locations.py --host example.com --network-id 12345 --username myusername --password mypassword`

## Washington Cities CSV File

To use this script, you will also need the `washington_cities.csv` file, which contains city data for Washington state. This file is included in this repository.

To download the file, either clone this repository using Git, or download the file directly from the GitHub website.

To clone the repository using Git, run the following command in your terminal:

`git clone https://github.com/fracticated/fwd.git`

This will create a local copy of the repository on your computer, including the `washington_cities.csv` file.

Alternatively, you can download the file directly from the GitHub website by following these steps:

1. Navigate to the repository on the GitHub website.
2. Click on the `washington_cities.csv` file in the file list.
3. Click the "Download" button to download the file.

Once you have downloaded the `washington_cities.csv` file, place it in the same directory as the `post_locations.py` script. Then, you can run the script using the instructions provided in the "Usage" section above.

## License

This script is released under the MIT License. See the LICENSE file for details.



