from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import os
import time
import json


@dataclass
class Business:
    """information data"""
    name: str = None
    phone_number: str = None
    address: str = None
    district: str = None    # Kecamatan
    city: str = None        # Kabupaten/Kota
    province: str = None    # Provinsi
    postal_code: str = None # Kode pos
    rating: float = None
    reviews: str = None
    latitude: float = None
    longitude: float = None
    location_link: str = None


@dataclass
class BusinessList:
    """Holds list of Business objects and provides methods to save data"""
    business_list: list[Business] = field(default_factory=list)
    save_at = "output"

    def dataframe(self):
        """Transforms business_list to pandas dataframe"""
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_"
        )

    def save_to_excel(self, filename):
        """Saves pandas dataframe to Excel (xlsx) file"""
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_excel(f"{self.save_at}/{filename}.xlsx", index=False)

    def save_to_csv(self, filename):
        """Saves pandas dataframe to CSV file"""
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_csv(f"{self.save_at}/{filename}.csv", index=False)


def extract_coordinates_from_url(url: str) -> tuple[float, float]:
    """Helper function to extract coordinates from a URL"""
    coordinates = url.split("!3d")[1].split("!4d")
    return float(coordinates[0]), float(coordinates[1].split('!')[0])

def format_phone_number(phone: str):
    """Format phone number to remove non-numeric characters and add country code if necessary."""
    if phone:
        # If the phone number contains parentheses (indicating it already has a region code), return it unchanged
        if '(' in phone and ')' in phone:
            return phone  # No change for numbers with parentheses (e.g., (0274) 367585)
        
        # Remove non-numeric characters
        phone = ''.join(filter(str.isdigit, phone))
        
        # If the number starts with '0', replace it with '62' (Indonesia country code)
        if phone.startswith("0"):
            phone = "62" + phone[1:]
        return phone
    return phone


# def load_config(config_file='config.json'):
#     """Load configuration from config.json"""
#     with open(config_file, 'r', encoding="utf-8") as file:
#         return json.load(file)

def load_config():
    """Load configuration from user input"""
    search_terms_input = input("Enter search terms separated by commas: ")
    search_terms = [term.strip() for term in search_terms_input.split(",")]

    max_results_input = input("Enter maximum results to scrape: ")
    try:
        max_results = int(max_results_input)
    except ValueError:
        print("Invalid input for max results, using default (1000).")
        max_results = 1000

    return {
        "search_terms": search_terms,
        "max_results": max_results
    }


def main():
    start_time = time.time()
    print("Script dimulai.")

    # Load configuration
    config = load_config()
    search_list = config.get("search_terms", [])
    total = config.get("max_results", 1000)

    ###########
    # Scraping
    ###########
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.google.com/maps", timeout=60000)
        page.wait_for_timeout(5000)

        for search_for_index, search_for in enumerate(search_list):
            print(f"-----\n{search_for_index} - {search_for}".strip())

            page.locator('//input[@id="searchboxinput"]').fill(search_for)
            page.wait_for_timeout(3000)
            page.keyboard.press("Enter")
            page.wait_for_timeout(5000)

            # Scrolling
            page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

            previously_counted = 0
            while True:
                page.mouse.wheel(0, 10000)
                page.wait_for_timeout(3000)

                if (
                    page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).count()
                    >= total
                ):
                    listings = page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).all()[:total]
                    listings = [listing.locator("xpath=..") for listing in listings]
                    print(f"Total Scraped: {len(listings)}")
                    break
                else:
                    if (
                        page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).count()
                        == previously_counted
                    ):
                        listings = page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).all()
                        print(
                            f"Arrived at all available\nTotal Scraped: {len(listings)}"
                        )
                        break
                    else:
                        previously_counted = page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).count()
                        print(
                            f"Currently Scraped: ",
                            page.locator(
                                '//a[contains(@href, "https://www.google.com/maps/place")]'
                            ).count(),
                        )

            business_list = BusinessList()

            for listing in listings:
                try:
                    listing.click()
                    page.wait_for_timeout(5000)

                    business = Business()
                    business.location_link = page.url
                    name_attribute = "aria-label"
                    name_xpath = '//h1[@class="DUwDvf lfPIob"]'
                    address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                    phone_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
                    review_count_xpath = "//div[2]/span[2]/span/span"
                    reviews_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'

                    if page.locator(name_xpath).count() > 0:
                        business.name = page.locator(name_xpath).inner_text()

                    if page.locator(address_xpath).count() > 0:
                        address = page.locator(address_xpath).inner_text()
                        business.address = address
                        # Pisahkan alamat berdasarkan koma
                        address_parts = address.split(",")
                        if len(address_parts) >= 4:
                            business.district = address_parts[-3].strip()  # Kecamatan
                            business.city = address_parts[-2].strip()      # Kabupaten/Kota
                            province_and_postal = address_parts[-1].strip()        # Provinsi + kode pos
                            business.province = " ".join(province_and_postal.split()[:-1])  # Nama provinsi tanpa kode pos
                            business.postal_code = province_and_postal[-5:]     # Kode Pos
                            # business.province = address_parts[-1].strip()   # Provinsi
                            # business.postal_code = business.province[-5:]  # Kode Pos
                        else:
                            business.district = business.city = business.province = business.postal_code = ""

                    if page.locator(phone_xpath).count() > 0:
                        business.phone_number = page.locator(phone_xpath).inner_text()
                        business.phone_number = format_phone_number(business.phone_number)

                    if page.locator(review_count_xpath).count() > 0:
                        business.reviews = str(
                            page.locator(review_count_xpath)
                            .get_attribute(name_attribute)
                            .split()[0]
                            .replace(".", "")
                            .strip()
                        )

                    if page.locator(reviews_xpath).count() > 0:
                        business.rating = float(
                            page.locator(reviews_xpath)
                            .get_attribute(name_attribute)
                            .split()[0]
                            .replace(",", ".")
                            .strip()
                        )

                    business.latitude, business.longitude = (
                        extract_coordinates_from_url(page.url)
                    )

                    business_list.business_list.append(business)
                except Exception as e:
                    print(f"Error occurred: {e}")

            #########
            # Output
            #########
            business_list.save_to_excel(
                f"google_maps_data_{search_for}".replace(" ", "_")
            )
            business_list.save_to_csv(
                f"google_maps_data_{search_for}".replace(" ", "_")
            )

        browser.close()

    end_time = time.time()
    total_duration = (end_time - start_time) / 60
    print(f"Script selesai dijalankan dalam {total_duration:.2f} Menit.")


if __name__ == "__main__":
    main()
