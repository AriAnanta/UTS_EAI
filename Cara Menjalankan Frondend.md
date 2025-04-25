## Cara Menjalankan Aplikasi

## Instalasi

1. Run semua layanan (Guest Service, Booking Service, Room Service, Payment Service)

2. Instal dependensi:

   ```
   pip install -r requirements.txt
   ```

3. Jalankan frontend:

   ```
   python app.py
   ```

4. Akses aplikasi di browser:
   ```
   http://localhost:5000
   ```

## Konfigurasi

Konfigurasi aplikasi frontend diatur melalui file .env di root direktori. Konfigurasi yang tersedia meliputi:

- `GUEST_SERVICE_URL` - URL untuk Guest Service (default: http://localhost:5001)
- `BOOKING_SERVICE_URL` - URL untuk Booking Service (default: http://localhost:5002)
- `ROOM_SERVICE_URL` - URL untuk Room Service (default: http://localhost:5003)
- `PAYMENT_SERVICE_URL` - URL untuk Payment Service (default: http://localhost:5004)

## Struktur Implementasi

Frontend dari aplikasi ini dibuat dengan menggunakan 4 microservice yang sudah dibuat, yaitu:

1. **Guest Service** - Mengelola data tamu dan profil
2. **Room Service** - Mengelola tipe kamar dan ketersediaannya
3. **Booking Service** - Mengelola reservasi dan pemesanan kamar
4. **Payment Service** - Mengelola transaksi pembayaran

## Simulasi Alur Pengguna

1. **Alur Pembuatan Booking**:

   - Cek ketersediaan kamar untuk tanggal tertentu
   - Pilih tipe kamar yang tersedia
   - Isi detail tamu (baru atau yang sudah ada)
   - Konfirmasi booking
   - Proses pembayaran

2. **Alur Manajemen Tamu**:

   - Tambah tamu baru
   - Lihat detail tamu dan riwayat booking
   - Update informasi tamu
   - Mengelola multiple booking untuk tamu yang sama

3. **Alur Manajemen Kamar**:
   - Tambah tipe kamar baru
   - Update informasi dan harga kamar
   - Cek ketersediaan dan status booking
   - Laporan okupansi
