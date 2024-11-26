import os
import pandas as pd
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dataclasses import dataclass
from typing import List
import json


@dataclass
class Business:
    """Represents a Business"""
    name: str = None
    phone: str = None
    category: str = None
    full_address: str = None
    district: str = None
    city: str = None
    province: str = None  # Provinsi
    postal_code: str = None  # Kode pos
    reviews_score: str = None
    reviews_amount: str = None
    latitude: float = None
    longitude: float = None
    googlemaps_link: str = None
    zone: str = None


class BusinessList:
    """Holds list of Business objects and provides methods to save data"""
    business_list: List[Business] = []  # Directly use list here
    save_at = "output"

    def dataframe(self):
        """Transforms business_list to pandas dataframe without 'category' and 'zone'."""
        # Convert dataclass objects to dictionary
        data = [business.__dict__ for business in self.business_list]
        # Exclude 'category' and 'zone' columns
        filtered_data = [{k: v for k, v in item.items() if k not in ['category', 'zone']} for item in data]
        # Convert to DataFrame
        return pd.DataFrame(filtered_data)

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


# Constants
INVALID_WEBSITE_NAMES = {}

def load_config():
    """Load configuration from user input."""
    
    # Meminta pengguna memasukkan kategori yang dipisahkan dengan koma
    categories_input = input("Masukkan kategori (pisahkan dengan koma): ")
    categories = [category.strip() for category in categories_input.split(",") if category.strip()]

    # Validasi apakah ada kategori yang dimasukkan
    if not categories:
        print("Kategori tidak boleh kosong.")
        return None

    # Meminta pengguna memasukkan lokasi target yang dipisahkan dengan koma
    target_locations_input = input("Masukkan lokasi target (pisahkan dengan koma): ")
    target_locations = [location.strip() for location in target_locations_input.split(",") if location.strip()]

    # Validasi apakah ada lokasi yang dimasukkan
    if not target_locations:
        print("Lokasi target tidak boleh kosong.")
        return None

    return {
        "categories": categories,
        "target_locations": target_locations
    }


def open_google_maps():
    # Open webdriver
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # for Chrome >= 109
    chrome_options.add_argument("--disable-usb-discovery")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://www.google.com/maps')
    print("⭐ Webdriver started")
    return driver


def wait_for_elements(driver, by, value, waittime=10):
    elements_present = EC.presence_of_all_elements_located((by, value))
    WebDriverWait(driver, 10).until(elements_present)


def search_for_category(driver, category, zone):
    # Input search category
    search = f"{category} en {zone}"
    searchbox = driver.find_element(By.ID, 'searchboxinput')
    searchbox.clear()
    searchbox.send_keys(str(search))
    search_button = driver.find_element(By.ID, 'searchbox-searchbutton')
    search_button.click()
    print(f"⭐ Searching {category} in {zone} ...")


def scroll_into_view(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)


def scroll_results(driver, current_amount_results, waittime=100):
    try:
        wait_for_elements(driver, By.CSS_SELECTOR, '.qjESne.veYFef')
        elemento = driver.find_element(By.CSS_SELECTOR, '.qjESne.veYFef')

        driver.execute_script("arguments[0].scrollIntoView(true);", elemento)

        times_left = 0
        print(f"⭐ {current_amount_results} results found ...")
        while times_left < waittime:
            try:
                wait_for_elements(driver, By.CSS_SELECTOR, '.hfpxzc')
                if int(current_amount_results) == int(len(driver.find_elements(By.CLASS_NAME, 'hfpxzc'))):
                    times_left += 1
                    time.sleep(0.1)
                else:
                    return True
            except:
                return False

        return False
    except:
        return False

def format_phone_number(phone: str):
    """Format phone number to remove non-numeric characters and add country code if necessary."""
    if phone:
        # If the phone number contains parentheses (indicating it already has a region code), return it unchanged
        if '024' in phone:
            return phone  # No change for numbers with parentheses (e.g., (0274) 367585)
        
        # Remove non-numeric characters
        phone = ''.join(filter(str.isdigit, phone))
        
        # If the number starts with '0', replace it with '62' (Indonesia country code)
        if phone.startswith("08"):
            phone = "62" + phone[1:]
        return phone
    return phone


def get_place_data(driver, place, previous_url, previous_name, category, location, business_list: BusinessList):
    # Scroll ke elemen
    scroll_into_view(driver, place)
    place.click()

    try:
        wait_for_elements(driver, By.CSS_SELECTOR, ".DUwDvf.lfPIob")
        place_name = re.sub(r"['\"&]", "", driver.find_element(By.CSS_SELECTOR, ".DUwDvf.lfPIob").text)
    except:
        place.click()
        wait_for_elements(driver, By.CSS_SELECTOR, ".DUwDvf.lfPIob")
        place_name = re.sub(r"['\"&]", "", driver.find_element(By.CSS_SELECTOR, ".DUwDvf.lfPIob").text)

    while not((previous_url == driver.current_url) == False and (previous_name == place_name) == False):
        place.click()
        time.sleep(0.3)
        wait_for_elements(driver, By.CSS_SELECTOR, ".DUwDvf.lfPIob")

        found = True
        while found:
            try:
                place_name = re.sub(r"['\"&]", "", driver.find_element(By.CSS_SELECTOR, ".DUwDvf.lfPIob").text)
                found = False
            except:
                place.click()
                time.sleep(0.3)


    # Nomor telepon
    try:
        place_phone_number = driver.find_element(By.CSS_SELECTOR, '[data-item-id^="phone:tel:"]').text
        place_phone_number = re.sub(r'[^\w\s,.()]', '', place_phone_number).strip()
        place_phone_number = format_phone_number(place_phone_number)
    except:
        place_phone_number = ""

    # Alamat
    try:
        address_element = driver.find_element(By.CSS_SELECTOR, '[data-item-id^="address"]')
        address = address_element.text
        address_parts = address.split(',')

        # Parsing alamat
        full_address = re.sub(r'[^\w\s,.]', '', address).strip()
        district = address_parts[-3].strip()  # Kecamatan
        city = address_parts[-2].strip()      # Kabupaten/Kota
        province_and_postal = address_parts[-1].strip()  # Provinsi + kode pos
        province = " ".join(province_and_postal.split()[:-1])  # Nama provinsi tanpa kode pos
        postal_code = province_and_postal.split()[-1] if province_and_postal.split()[-1].isdigit() else ""
    except:
        full_address = district = city = province = postal_code = ""

    # Koordinat (latitude, longitude)
    match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", driver.current_url)
    if match:
        latitude, longitude = float(match.group(1)), float(match.group(2))
    else:
        latitude, longitude = None, None

    # Review score dan jumlah review
    try:
        place_review_score = re.sub(r"[,]", ".", driver.find_element(By.CSS_SELECTOR, 'div.F7nice span[aria-hidden="true"]').text)
        place_review_amount = int(re.sub(r"[(\")\".]", "", driver.find_element(By.CSS_SELECTOR, 'div.F7nice span:nth-child(2) span[aria-label]').text))
    except:
        place_review_score = ""
        place_review_amount = ""

    # Buat objek Business
    business = Business(
        name=place_name,
        phone=place_phone_number,
        category=category,
        full_address = full_address,
        district=district,
        city=city,
        province=province,
        postal_code=postal_code,
        reviews_score=place_review_score,
        reviews_amount=place_review_amount,
        latitude=latitude,
        longitude=longitude,
        googlemaps_link=driver.current_url,
        zone=location
    )

    # Tambahkan objek ke business_list
    business_list.business_list.append(business)

    return business


def main():
    start_time = time.time()
    print("Script dimulai.")
    
    config = load_config()
    
    business_list = BusinessList()

    # Main logic
    driver = open_google_maps()
    wait_for_elements(driver, By.CLASS_NAME, 'searchboxinput')

    last_place = ""
    last_url = ""
    count = 0

    for category in config['categories']:
        for location in config['target_locations']:
            search_for_category(driver, category, location)
            wait_for_elements(driver, By.CLASS_NAME, 'hfpxzc')

            discovered_places = 0
            while True:
                try:
                    available_places = len(driver.find_elements(By.CLASS_NAME, 'hfpxzc'))
                    if available_places == discovered_places:
                        if scroll_results(driver, available_places) == False:
                            break
                    else:
                        discovered_places = len(driver.find_elements(By.CLASS_NAME, 'hfpxzc'))
                except TimeoutException:
                    print("❓ Not found")
                    break

            places = driver.find_elements(By.CLASS_NAME, 'hfpxzc')

            for place in places:
                place_data = get_place_data(driver, place, last_url, last_place, category, location, business_list)
                while last_url == driver.current_url:
                    print("Please Wait..")
                    last_url = driver.current_url
                last_place = place_data.name
                count += 1
                last_url = driver.current_url
                print(f"📩 {count} | Stored {place_data.name}")

    # After all the data is collected, save it to a file
    file_name = f"google_maps_{location}".replace(" ", "_")  # Proses nama file
    business_list.save_to_excel(file_name)  # Save to Excel
    business_list.save_to_csv(file_name)    # Save to CSV

    # Close the browser after processing
    driver.quit()

    end_time = time.time()
    total_duration = (end_time - start_time) / 60
    print(f"Script selesai dijalankan dalam {total_duration:.2f} Menit.")


if __name__ == "__main__":
    print("Halo Haloo")
    main()
