# Google Maps Scraper V2.0

Google Maps Business Scraper adalah sebuah alat otomatisasi berbasis Python yang memungkinkan pengumpulan data bisnis dari Google Maps berdasarkan kategori dan lokasi yang ditentukan oleh pengguna. Data yang dikumpulkan mencakup informasi seperti nama bisnis, nomor telepon, alamat lengkap, koordinat, dan ulasan.

## Fitur
- **Pengumpulan data bisnis**: Informasi seperti nama bisnis, nomor telepon, kategori, alamat lengkap, kota, provinsi, kode pos, koordinat geografis, skor ulasan, dan jumlah ulasan.
- **Format keluaran**: Data disimpan dalam format **Excel (.xlsx)** dan **CSV (.csv)**.
- **Kategori dan lokasi kustom**: Pengguna dapat menentukan kategori bisnis dan lokasi target melalui input terminal.
- **Pemrosesan otomatis**: Skrip menggunakan Selenium WebDriver untuk navigasi otomatis pada Google Maps.

## Persyaratan
Sebelum menjalankan skrip, pastikan Anda telah menginstal dependensi berikut:
- Python 3.7 atau lebih baru
- Google Chrome
- ChromeDriver

## Instalasi
1. Clone repositori ini atau unduh skrip.
    ```bash
   git clone 
   ```
2. Instal dependensi Python:
   ```bash
   pip install -r requirements.txt
   ```

## Running
1. Jalankan skrip dengan:
    ```bash
    python App_2.0.py
    ```
2. Masukkan kategori bisnis dan lokasi target yang ingin dicari, dipisahkan dengan koma. Contoh:
    ```bash
    Masukkan kategori (pisahkan dengan koma): Toko Bahan Bangunan
    Masukkan lokasi target (pisahkan dengan koma): Semarang
    ```
3. Skrip akan otomatis memulai pengumpulan data dari Google Maps. Data akan disimpan dalam format Excel dan CSV di folder output.

## Struktur Output
Struktur output akan memiliki atribut berikut:
- name
- phone
- full_address
- district
- city
- province
- postal_code
- reviews_score
- reviews_amount
- latitude
- longitude
- googlemaps_link

## Disclaimer
Harap gunakan skrip ini secara bertanggung jawab dan periksa Ketentuan Layanan Google Maps sebelum melakukan scraping dalam skala besar.
