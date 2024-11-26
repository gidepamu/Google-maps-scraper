# Google Maps Scraper

This Python code is a web scraper that uses Playwright to extract business data from Google Maps. The code is designed to search for businesses based on user-specified keywords, collect relevant data, and save it in CSV or Excel formats.

### Features:

*   Searches Google Maps for specified terms
*   Efficiently scrolls through results for expanded data collection
*   Extracts the following information for each business listing:
    *   Name
    *   Address
    *   District
    *   Regency/City
    *   State/Province
    *   Postal Code
    *   Phone Number
    *   Reviews Count
    *   Reviews Average
    *   Latitude
    *   Longitude
    *   Location Link
*   Saves results in both Excel (.xlsx) and CSV formats.

## Installation of Requirements

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/gidepamu/Google-maps-scraper.git
   ```

2. Install the dependencies using the requirements.txt file:

   ```bash
   pip install -r requirements.txt
   ```

##  Running the Script
1. Run App.py
    ```bash
   python App.py
   ```

2. Passing Search Term as Argument, Example:
    ```bash
    Enter search terms separated by commas: Toko Bahan Bangunan Kota Semarang
    Enter maximum results to scrape: 5
    ```
`This will search for building market stores in Semarang City and collect up to 5 listings.`

##  Example Output:

The saved Excel and CSV files will contain a structured table with the collected business information.

##  Disclaimer

Please use this script responsibly and check the Google Maps Terms of Service before large-scale scraping. 
