# DOKUMENTASI API APLIKASI HOTEL

## Overview

Sistem manajemen pemesanan hotel berbasis microservices yang dibangun dengan Flask dan MySQL. Sistem ini terdiri dari empat layanan inti yang beroperasi secara independen sambil berkomunikasi melalui API HTTP untuk memberikan pengalaman pemesanan hotel yang terintegrasi, efisien, dan terverifikasi.

## Core Service

### 1. Guest Service

**Tujuan:** Mengelola data tamu hotel
**Endpoint Utama:** `/guests`

**Fitur:**

- Menambah tamu baru dengan validasi duplikat (UID tamu & email)
- Melihat daftar tamu aktif (dengan soft delete)
- Memperbarui data tamu
- Menghapus tamu (dengan validasi pemesanan masa depan)
- Melihat riwayat pemesanan tamu melalui Layanan Pemesanan

### 2. Room Service

**Tujuan:** Mengelola informasi tipe kamar hotel
**Endpoint Utama:** `/rooms`

**Fitur:**

- Menambah tipe kamar baru
- Melihat semua tipe kamar aktif
- Memperbarui detail tipe kamar
- Menonaktifkan tipe kamar (soft delete, dengan validasi pemesanan aktif)
- Memeriksa ketersediaan kamar berdasarkan tanggal (`/rooms/<type_code>/availability`)

### 3. Booking Service

**Tujuan:** Mengelola pemesanan kamar oleh tamu
**Endpoint Utama:** `/bookings`

**Fitur:**

- Membuat pemesanan baru (dengan validasi tamu & kamar)
- Memicu permintaan pembayaran otomatis
- Mendapatkan daftar pemesanan berdasarkan tamu atau tipe kamar
- Konfirmasi pembayaran manual
- Pembatalan pemesanan dengan validasi kebijakan
- Detail pemesanan berdasarkan UID

### 4. Payment Service

**Tujuan:** Mensimulasikan transaksi pembayaran dan memperbarui status pemesanan
**Endpoint Utama:** `/payments`

**Fitur:**

- Memverifikasi status pemesanan dan tamu sebelum pembayaran
- Mensimulasikan proses pembayaran dengan probabilitas keberhasilan
- Pembaruan status pemesanan otomatis
- Melihat status transaksi berdasarkan UID pembayaran
- Mengambil daftar semua transaksi

## Integrasi lanayan

### Konfigurasi

- Semua layanan menggunakan URL yang dapat dikonfigurasi (melalui os.environ) untuk komunikasi antar layanan

### Poin Integrasi

1. **Payment Service:**

   - Memvalidasi dengan Layanan Tamu & Layanan Kamar untuk pemesanan baru
   - Memicu Layanan Pembayaran untuk pemrosesan pembayaran

2. **Booking Service:**

   - Memvalidasi data pemesanan & tamu sebelum memproses
   - Memperbarui status pemesanan di Layanan Pemesanan setelah berhasil

3. **Guest Service & Room Service:**
   - Memeriksa dengan Layanan Pemesanan sebelum soft deletions

## Technology Stack

- **Framework:** Flask (REST API)
- **Database:** MySQL (via SQLAlchemy ORM)
- **Service Communication:** REST (HTTP Request)
- **Architecture:** Independent & scalable microservices

## Dokumentasi Komunikasi Antar Layanan (Implementasi)

### Gambaran Sistem

Sistem hotel ini terdiri dari 4 layanan mikro yang saling terhubung:

1. **Layanan Tamu** (port 5001) - Pengelolaan data tamu
2. **Layanan Pemesanan** (port 5002) - Pengelolaan pemesanan kamar
3. **Layanan Kamar** (port 5003) - Pengelolaan tipe kamar dan ketersediaan
4. **Layanan Pembayaran** (port 5004) - Pengelolaan transaksi pembayaran

### Diagram Komunikasi Layanan

```
Layanan Tamu (5001)      Layanan Kamar (5003)
       ↑     ↓                   ↑     ↓
       ↑     ↓                   ↑     ↓
Layanan Pembayaran (5004) ←→ Layanan Pemesanan (5002)
```

### Interaksi Antar Layanan

#### 1. Payment Service → Guest Service

**Tujuan:** Memvalidasi keberadaan dan status aktif tamu sebelum pemesanan
**Endpoint:** `GET /guests/{guest_uid}`

**Implementasi:**

```python
def validate_guest(guest_uid):
    try:
        response = requests.get(f"{GUEST_SERVICE_URL}/guests/{guest_uid}", timeout=5)
        if response.ok: return True, response.json()
        elif response.status_code == 404: return False, {"error": "Tamu tidak ditemukan atau tidak aktif"}
        else: response.raise_for_status()
    except requests.exceptions.Timeout: return False, {"error": "Timeout layanan tamu"}
    except requests.RequestException as e: return False, {"error": f"Kesalahan layanan tamu: {str(e)}"}
```

**Alur Proses:**

1. Layanan Pemesanan mengirim permintaan ke Layanan Tamu
2. Layanan Tamu memeriksa database tamu aktif
3. Mengembalikan data tamu jika valid dan aktif
4. Mengembalikan error jika tidak valid

**Penanganan Error:**

- 503: Layanan Tidak Tersedia (Timeout)
- 404: Tamu Tidak Ditemukan
- 500: Kesalahan Internal Server

#### 2. Payment Service → Room Service

**Tujuan:** Memvalidasi tipe kamar dan mendapatkan harga per malam
**Endpoint:** `GET /rooms/{type_code}`

**Implementasi:**

```python
def get_room_details(room_type_code):
    try:
        response = requests.get(f"{ROOM_SERVICE_URL}/rooms/{room_type_code}", timeout=5)
        if response.ok: return True, response.json()
        elif response.status_code == 404: return False, {"error": f"Tipe kamar '{room_type_code}' tidak ditemukan atau tidak aktif"}
        else: response.raise_for_status()
    except requests.exceptions.Timeout: return False, {"error": "Timeout layanan kamar"}
    except requests.RequestException as e: return False, {"error": f"Kesalahan layanan kamar: {str(e)}"}
```

**Alur Proses:**

1. Layanan Pemesanan mengirim permintaan ke Layanan Kamar
2. Layanan Kamar memeriksa database tipe kamar aktif
3. Mengembalikan detail kamar termasuk harga jika valid
4. Mengembalikan error jika tidak valid

**Penanganan Error:**

- 503: Layanan Tidak Tersedia (Timeout)
- 404: Tipe Kamar Tidak Ditemukan
- 500: Kesalahan Internal Server

#### 3. Booking Service → Payment Service

**Tujuan:** Memicu proses pembayaran setelah pemesanan dibuat
**Endpoint:** `POST /payments`

**Implementasi:**

```python
def trigger_payment(booking_uid, amount):
    try:
        payload = {"booking_uid": booking_uid, "amount": amount}
        response = requests.post(f"{PAYMENT_SERVICE_URL}/payments", json=payload, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.Timeout: return False, {"error": "Timeout layanan pembayaran"}
    except requests.RequestException as e: return False, {"error": f"Kesalahan layanan pembayaran: {str(e)}"}
```

**Alur Proses:**

1. Layanan Pemesanan mengirim data pemesanan ke Layanan Pembayaran
2. Layanan Pembayaran memvalidasi data
3. Layanan Pembayaran membuat transaksi dan memproses pembayaran
4. Hasil pembayaran dikembalikan ke Layanan Pemesanan

**Penanganan Error:**

- 503: Layanan Tidak Tersedia (Timeout)
- 400: Data Tidak Valid
- 500: Kesalahan Internal Server

#### 4. Payment Service → Booking Service

**Endpoints:**

- `GET /bookings/{booking_uid}` (untuk validasi)
- `PUT /bookings/{booking_uid}/confirm-payment` (untuk memperbarui status)

**Tujuan:**

1. Memvalidasi pemesanan sebelum memproses pembayaran
2. Memperbarui status pemesanan setelah pembayaran berhasil

**Implementasi:**

```python
# Validasi pemesanan
booking_url = f"{BOOKING_SERVICE_URL}/bookings/{booking_uid}"
booking_response = requests.get(booking_url, timeout=5)
```

```python
# Memperbarui status pemesanan
update_url = f"{BOOKING_SERVICE_URL}/bookings/{booking_uid}/confirm-payment"
update_data = {"payment_uid": payment_uid, "amount": amount_float}
update_response = requests.put(update_url, json=update_data, timeout=5)
```

**Alur Proses:**

1. Layanan Pembayaran memverifikasi pemesanan sebelum memproses pembayaran
2. Setelah pembayaran berhasil, Layanan Pembayaran memperbarui status pemesanan
3. Layanan Pemesanan menerima pembaruan dan menyimpan status baru

**Penanganan Error:**

- 400: Pemesanan Tidak Valid
- 503: Layanan Tidak Tersedia (Timeout)
- 500: Kesalahan Internal Server

#### 5. Guest Service → Booking Service

**Tujuan:** Memeriksa pemesanan aktif sebelum menghapus tamu
**Endpoint:** `GET /bookings?guest_uid={guest_uid}&status=confirmed`

**Implementasi:**

```python
def check_guest_bookings(guest_uid):
    booking_check_url = f"{BOOKING_SERVICE_URL}/bookings?guest_uid={guest_uid}&status=confirmed"
    response = requests.get(booking_check_url, timeout=5)
    return response.json()
```

**Alur Proses:**

1. Layanan Tamu memeriksa apakah tamu memiliki pemesanan aktif
2. Layanan Pemesanan mengembalikan daftar pemesanan yang sesuai
3. Penghapusan tamu ditolak jika ada pemesanan aktif

**Penanganan Error:**

- 503: Layanan Tidak Tersedia (Timeout)
- 500: Kesalahan Internal Server

#### 6. Room Service → Booking Service

**Tujuan:** Memeriksa pemesanan aktif sebelum menonaktifkan tipe kamar
**Endpoint:** `GET /bookings/by-room?room_type_code={type_code}`

**Implementasi:**

```python
def check_room_bookings(type_code):
    booking_check_url = f"{BOOKING_SERVICE_URL}/bookings/by-room?room_type_code={type_code}"
    response = requests.get(booking_check_url, timeout=10)
    return response.json()
```

**Alur Proses:**

1. Layanan Kamar memeriksa pemesanan aktif untuk tipe kamar
2. Layanan Pemesanan mengembalikan daftar pemesanan yang sesuai
3. Penonaktifan tipe kamar ditolak jika ada pemesanan aktif

**Penanganan Error:**

- 503: Layanan Tidak Tersedia (Timeout)
- 500: Kesalahan Internal Server

## Pola Komunikasi

### 1. Panggilan HTTP Sinkron

Semua komunikasi menggunakan pola permintaan-respons sinkron

### 2. Penanganan Timeout

Setiap panggilan layanan memiliki pengaturan timeout yang jelas (umumnya 5-10 detik)

### 3. Propagasi Error

Error dari layanan lain diteruskan ke klien dengan kode status yang sesuai

### 4. Penanganan Error

- Untuk operasi kritis (mis. validasi pemesanan), sistem menggunakan fail-closed (menolak operasi jika validasi gagal)
- Untuk operasi non-kritis (mis. cek ketersediaan), sistem menggunakan fail-open (mengasumsikan tersedia jika validasi gagal)

# Dokumentasi API Hotel Management System

## Daftar isi

- [Guest Service (Port 5001)](#guest-service)
- [Booking Service (Port 5002)](#booking-service)
- [Room Service (Port 5003)](#room-service)
- [Payment Service (Port 5004)](#payment-service)

## Guest Service

### Create Guest

- **Endpoint**: `POST /guests`
- **Port**: 5001
- **Request Body**:

```json
{
    "guest_uid": "string",
    "name": "string",
    "email": "string",
    "phone": "string" (optional)
}
```

- **Validasi Input**:

  - `guest_uid`: Wajib diisi, harus unik (tidak boleh duplikat dengan tamu aktif)
  - `name`: Wajib diisi, tidak boleh kosong
  - `email`: Wajib diisi, format email valid, harus unik (tidak boleh duplikat dengan tamu aktif)
  - `phone`: Opsional

- **Success Response** (201):

```json
{
  "message": "Data tamu berhasil dibuat",
  "guest": {
    "guest_uid": "string",
    "name": "string",
    "email": "string",
    "phone": "string"
  }
}
```

- **Error Responses**:
  - **400 Bad Request**:
    ```json
    {
      "error": "Data tidak lengkap (membutuhkan guest_uid, name, email)"
    }
    ```
  - **409 Conflict** (Guest UID duplikat):
    ```json
    {
      "error": "Guest UID 'G12345' aktif sudah ada"
    }
    ```
  - **409 Conflict** (Email duplikat):
    ```json
    {
      "error": "Email 'email@example.com' aktif sudah terdaftar"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Gagal menyimpan data tamu",
      "details": "[pesan error database]"
    }
    ```

### Get All Guests

- **Endpoint**: `GET /guests`
- **Success Response** (200):

```json
[
  {
    "guest_uid": "string",
    "name": "string",
    "email": "string",
    "phone": "string"
  }
]
```

- **Error Responses**:
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Kesalahan database saat mengambil daftar tamu",
      "details": "[pesan error database]"
    }
    ```

### Get Guest by UID

- **Endpoint**: `GET /guests/{guest_uid}`
- **Validasi Path Parameter**:

  - `guest_uid`: Wajib diisi, harus ada dalam database dan statusnya aktif

- **Success Response** (200):

```json
{
  "guest_uid": "string",
  "name": "string",
  "email": "string",
  "phone": "string"
}
```

- **Error Responses**:
  - **404 Not Found**:
    ```json
    {
      "error": "Tamu aktif tidak ditemukan"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Kesalahan database saat mengambil data tamu",
      "details": "[pesan error database]"
    }
    ```

### Update Guest

- **Endpoint**: `PUT /guests/{guest_uid}`
- **Validasi Path Parameter**:

  - `guest_uid`: Wajib diisi, harus ada dalam database dan statusnya aktif

- **Request Body**:

```json
{
    "name": "string" (optional),
    "email": "string" (optional),
    "phone": "string" (optional)
}
```

- **Validasi Input**:

  - Request body tidak boleh kosong
  - `email`: Jika diisi, harus unik (tidak boleh duplikat dengan tamu aktif lain)

- **Success Response** (200):

```json
{
  "message": "Data tamu berhasil diperbarui",
  "guest": {
    "guest_uid": "string",
    "name": "string",
    "email": "string",
    "phone": "string"
  }
}
```

- **Error Responses**:
  - **400 Bad Request**:
    ```json
    {
      "error": "Request body tidak boleh kosong"
    }
    ```
  - **404 Not Found**:
    ```json
    {
      "error": "Tamu aktif tidak ditemukan untuk diperbarui"
    }
    ```
  - **409 Conflict** (Email duplikat):
    ```json
    {
      "error": "Email 'email@example.com' sudah digunakan tamu aktif lain"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Gagal memperbarui data tamu",
      "details": "[pesan error database]"
    }
    ```

### Get Guest's Bookings

- **Endpoint**: `GET /guests/{guest_uid}/bookings`
- **Validasi Path Parameter**:

  - `guest_uid`: Wajib diisi, harus ada dalam database dan statusnya aktif

- **Success Response** (200):

```json
[
  {
    "booking_uid": "string",
    "room_type_code": "string",
    "check_in_date": "YYYY-MM-DD",
    "check_out_date": "YYYY-MM-DD",
    "total_price": 800000,
    "status": "confirmed",
    "booking_time": "2023-12-20T10:00:00Z"
  }
]
```

- **Error Responses**:
  - **404 Not Found**:
    ```json
    {
      "error": "Tamu aktif tidak ditemukan"
    }
    ```
  - **503 Service Unavailable**:
    ```json
    {
      "error": "Gagal mengambil data pemesanan dari BookingService",
      "details": "Timeout"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Kesalahan sistem saat memproses riwayat pemesanan"
    }
    ```

### Delete Guest

- **Endpoint**: `DELETE /guests/{guest_uid}`
- **Validasi Path Parameter**:

  - `guest_uid`: Wajib diisi, harus ada dalam database dan statusnya aktif
  - Tamu tidak boleh memiliki booking aktif di masa depan

- **Success Response** (200):

```json
{
  "message": "Data tamu berhasil dihapus"
}
```

- **Error Responses**:
  - **404 Not Found**:
    ```json
    {
      "error": "Tamu aktif tidak ditemukan untuk dihapus"
    }
    ```
  - **409 Conflict** (Ada booking aktif):
    ```json
    {
      "error": "Tidak dapat menghapus tamu karena memiliki booking aktif mendatang",
      "booking_count": 2
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Gagal menghapus data tamu",
      "details": "[pesan error database]"
    }
    ```

## Booking Service

### Create Booking

- **Endpoint**: `POST /bookings`
- **Request Body**:

```json
{
  "guest_uid": "string (required)",
  "room_type_code": "string (required)",
  "check_in": "string (required, format YYYY-MM-DD)",
  "check_out": "string (required, format YYYY-MM-DD)"
}
```

- **Validasi**:

  - Semua field wajib diisi
  - `guest_uid` harus valid dan aktif di Guest Service
  - `room_type_code` harus valid dan aktif di Room Service
  - `check_in` dan `check_out` harus format tanggal valid
  - `check_out` harus setelah `check_in`
  - `check_in` tidak boleh di masa lalu

- **Success Response** (201):

```json
{
    "booking_uid": "string",
    "guest_uid": "string",
    "room_type_code": "string",
    "check_in_date": "YYYY-MM-DD",
    "check_out_date": "YYYY-MM-DD",
    "total_price": number,
    "status": "pending_payment",
    "booking_time": "datetime"
}
```

- **Error Responses**:
  - **400 Bad Request** (Data tidak lengkap):
    ```json
    {
      "error": "Data tidak lengkap (guest_uid, room_type_code, check_in, check_out)"
    }
    ```
  - **400 Bad Request** (Tanggal tidak valid):
    ```json
    {
      "error": "Tanggal check-in/check-out tidak valid"
    }
    ```
  - **400 Bad Request** (Format tanggal salah):
    ```json
    {
      "error": "Format tanggal tidak valid (YYYY-MM-DD)"
    }
    ```
  - **404 Not Found** (Tipe kamar tidak ditemukan):
    ```json
    {
      "error": "Tipe kamar 'deluxe' tidak ditemukan atau tidak aktif"
    }
    ```
  - **503 Service Unavailable** (Layanan tamu tidak tersedia):
    ```json
    {
      "error": "Timeout hubungi GuestService"
    }
    ```
  - **503 Service Unavailable** (Layanan kamar tidak tersedia):
    ```json
    {
      "error": "Gagal hubungi RoomService",
      "details": "[pesan error]"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Gagal menyimpan data pemesanan",
      "details": "[pesan error database]"
    }
    ```
  - **207 Multi-Status** (Booking dibuat tapi gagal update status):
    ```json
    {
        "booking_uid": "string",
        "guest_uid": "string",
        "room_type_code": "string",
        "check_in_date": "YYYY-MM-DD",
        "check_out_date": "YYYY-MM-DD",
        "total_price": number,
        "status": "pending_payment",
        "booking_time": "datetime",
        "warning": "Booking dibuat, tetapi gagal mengupdate status setelah pembayaran."
    }
    ```

### Get All Bookings

- **Endpoint**: `GET /bookings`
- **Query Parameters**:

  - `guest_uid` (optional): Filter booking berdasarkan tamu
  - `status` (optional): Filter booking berdasarkan status

- **Success Response** (200): 
```json
[
    {
        "booking_time": "2025-04-24T00:08:33Z",
        "booking_uid": "9801ca08-3413-4fc7-9561-d86c4f00c15f",
        "check_in_date": "2025-04-24",
        "check_out_date": "2025-04-30",
        "guest_uid": "GUEST107",
        "payment_id": "pay_f8df7cc2-a21d-48b6-acc6-3eebdcc3871e",
        "room_type_code": "rt015",
        "status": "confirmed",
        "total_price": 4800000.0
    },
    {
        "booking_time": "2025-04-16T11:00:00Z",
        "booking_uid": "BOOK112",
        "check_in_date": "2025-06-25",
        "check_out_date": "2025-06-27",
        "guest_uid": "GUEST112",
        "payment_id": null,
        "room_type_code": "RT012",
        "status": "pending_payment",
        "total_price": 1400000.0
    }
]
```
- **Error Responses**:
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Kesalahan DB",
      "details": "[pesan error database]"
    }
    ```

### Get Booking by UID

- **Endpoint**: `GET /bookings/{booking_uid}`
- **Validasi Path Parameter**:

  - `booking_uid`: Wajib diisi, harus ada dalam database

- **Success Response** (200): 
``` json
{
    "booking_time": "2025-04-16T11:00:00Z",
    "booking_uid": "BOOK112",
    "check_in_date": "2025-06-25",
    "check_out_date": "2025-06-27",
    "guest_uid": "GUEST112",
    "payment_id": null,
    "room_type_code": "RT012",
    "status": "pending_payment",
    "total_price": 1400000.0
}
```
- **Error Responses**:
  - **404 Not Found**:
    ```json
    {
      "error": "Tidak ditemukan"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Kesalahan DB",
      "details": "[pesan error database]"
    }
    ```

### Cancel Booking

- **Endpoint**: `PUT /bookings/{booking_uid}/cancel`
- **Validasi Path Parameter**:

  - `booking_uid`: Wajib diisi, harus ada dalam database
  - Booking harus dalam status yang dapat dibatalkan ('confirmed' atau 'pending_payment')
  - Pembatalan tidak diizinkan pada H-1 check-in

- **Request Body**:

```json
{
    "reason": "string" 
}
```

- **Success Response** (200):
```json
{
    "booking_time": "2025-04-15T18:00:00Z",
    "booking_uid": "BOOK109",
    "cancellation_reason": "Pengen aja",
    "cancelled_at": "2025-04-24T03:00:35Z",
    "check_in_date": "2025-06-10",
    "check_out_date": "2025-06-12",
    "guest_uid": "GUEST109",
    "payment_id": "PAY105",
    "room_type_code": "RT019",
    "status": "cancelled",
    "total_price": 4000000.0
}
```

- **Error Responses**:
  - **404 Not Found**:
    ```json
    {
      "error": "Pemesanan tidak ditemukan"
    }
    ```
  - **409 Conflict** (Status tidak dapat dibatalkan):
    ```json
    {
      "error": "Booking dengan status 'cancelled' tidak dapat dibatalkan"
    }
    ```
  - **400 Bad Request** (Terlambat membatalkan):
    ```json
    {
      "error": "Pembatalan tidak diizinkan setelah atau pada 2023-12-14 (H-1 check-in)"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Gagal membatalkan booking",
      "details": "[pesan error database]"
    }
    ```

### Confirm Payment

- **Endpoint**: `PUT /bookings/{booking_uid}/confirm-payment`
- **Request Body**:

```json
{
  "payment_uid": "string",
  "amount": 800000
}
```

- **Validasi Input**:

  - `booking_uid`: Harus ada di database
  - `payment_uid`: Harus unik
  - `amount`: Harus sesuai dengan total_price pemesanan

- **Success Response** (200):

```json
{
  "message": "Booking berhasil dikonfirmasi",
  "booking": {
    "booking_uid": "string",
    "status": "confirmed",
    "payment_id": "pay_abc123"
  }
}
```

- **Error Responses**:
  - **400 Bad Request**:
    ```json
    {
      "error": "Jumlah pembayaran (750000) tidak sesuai dengan tagihan (800000)"
    }
    ```
  - **404 Not Found**:
    ```json
    {
      "error": "Booking tidak ditemukan"
    }
    ```
  - **409 Conflict**:
    ```json
    {
      "error": "Booking dengan status 'cancelled' tidak dapat dikonfirmasi"
    }
    ```

### Get Bookings by Room Type

- **Endpoint**: `GET /bookings/by-room`
- **Port**: 5002
- **Query Parameters**:

  - `room_type_code`: (string, required) Kode tipe kamar (case-insensitive)
  - `status`: (string, optional) Filter berdasarkan status pemesanan (confirmed, cancelled, dll.)

- **Success Response** (200):

```json
[
  {
    "booking_uid": "b_12345",
    "guest_uid": "g_67890",
    "room_type_code": "deluxe",
    "check_in_date": "2023-12-25",
    "check_out_date": "2023-12-30",
    "total_price": 4000000,
    "status": "confirmed",
    "booking_time": "2023-11-20T14:30:00Z"
  }
]
```

- **Error Responses**:
  - **400 Bad Request**:
    ```json
    {
      "error": "Parameter room_type_code wajib disertakan"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Kesalahan DB",
      "details": "[pesan error]"
    }
    ```

## Room Service

### Create Room Type

- **Endpoint**: `POST /rooms`
- **Request Body**:

```json
{
    "type_code": "string",
    "name": "string",
    "description": "string" (optional),
    "price_per_night": number
}
```

- **Validasi Input**:

  - `type_code`: Wajib diisi, harus unik (tidak boleh duplikat dengan tipe kamar aktif)
  - `name`: Wajib diisi
  - `price_per_night`: Wajib diisi, harus angka positif

- **Success Response** (201):

```json
[
  {
    "status": "ok",
    "message": "Kamar deluxe berhasil ditambahkan."
  },
  {
    "type_code": "deluxe",
    "name": "Deluxe Room",
    "description": "Kamar mewah dengan pemandangan kota",
    "price_per_night": 800000
  }
]
```

- **Error Responses**:
  - **400 Bad Request** (Data tidak lengkap):
    ```json
    {
      "error": "Data tidak lengkap (type_code, name, price_per_night)"
    }
    ```
  - **409 Conflict** (Tipe kamar duplikat):
    ```json
    {
      "error": "Tipe kamar aktif dengan kode 'deluxe' sudah ada"
    }
    ```
  - **400 Bad Request** (Harga tidak valid):
    ```json
    {
      "error": "Nilai price_per_night tidak valid atau tidak positif"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Gagal menyimpan tipe kamar",
      "details": "[pesan error database]"
    }
    ```

### Get All Room Types

- **Endpoint**: `GET /rooms`
- **Success Response** (200):
``` json
[
    {
        "description": "Kamar dengan tempat tidur bertingkat",
        "name": "Bunk Room",
        "price_per_night": 500000.0,
        "type_code": "RT020"
    },
    {
        "description": "Kamar yang terhubung untuk keluarga",
        "name": "Connecting Room",
        "price_per_night": 800000.0,
        "type_code": "RT015"
    }
]
```
- **Error Responses**:
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Kesalahan database saat mengambil tipe kamar",
      "details": "[pesan error database]"
    }
    ```

### Get Room Type Details

- **Endpoint**: `GET /rooms/{type_code}`
- **Validasi Path Parameter**:

  - `type_code`: Wajib diisi, harus ada dalam database dan statusnya aktif

- **Success Response** (200): 
```json
{
    "description": "Suite kecil dengan fasilitas premium",
    "name": "Junior Suite",
    "price_per_night": 950000.0,
    "type_code": "RT011"
}
```
- **Error Responses**:
  - **404 Not Found**:
    ```json
    {
      "error": "Tipe kamar aktif 'presidential' tidak ditemukan"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Kesalahan database saat mengambil detail kamar",
      "details": "[pesan error database]"
    }
    ```

### Check Room Availability

- **Endpoint**: `GET /rooms/{type_code}/availability`
- **Validasi Path Parameter**:

  - `type_code`: Wajib diisi, harus ada dalam database dan statusnya aktif

- **Query Parameters**:(Masukan hal ini di bagian parameter)

  - check_in: Wajib diisi, format tanggal valid (YYYY-MM-DD)
  - check_out: Wajib diisi, format tanggal valid (YYYY-MM-DD), harus setelah check_in

- **Success Response** (200):

```json
{
    "type_code": "string",
    "available": boolean,
    "available_count": number,
    "total_rooms": number,
    "check_in": "YYYY-MM-DD",
    "check_out": "YYYY-MM-DD",
    "message": "string"
}
```

- **Error Responses**:
  - **400 Bad Request** (Parameter tidak lengkap):
    ```json
    {
      "error": "Parameter check_in dan check_out diperlukan"
    }
    ```
  - **400 Bad Request** (Tanggal tidak valid):
    ```json
    {
      "error": "check_out harus setelah check_in"
    }
    ```
  - **400 Bad Request** (Format tanggal salah):
    ```json
    {
      "error": "Format tanggal tidak valid (YYYY-MM-DD)"
    }
    ```
  - **404 Not Found**:
    ```json
    {
      "error": "Tipe kamar tidak aktif atau tidak ditemukan"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Kesalahan saat memeriksa ketersediaan",
      "details": "[pesan error]"
    }
    ```

### Delete Room Type

- **Endpoint**: `DELETE /rooms/{type_code}`
- **Validasi Path Parameter**:

  - `type_code`: Wajib diisi, harus ada dalam database dan statusnya aktif
  - Tidak boleh ada booking aktif dengan check_out_date di masa depan

- **Success Response** (200):

```json
{
  "message": "Tipe kamar deluxe berhasil dinonaktifkan",
  "room_type": {
    "type_code": "deluxe",
    "name": "Deluxe Room",
    "description": "Kamar mewah dengan pemandangan kota",
    "price_per_night": 800000,
    "is_active": false
  }
}
```

- **Error Responses**:
  - **404 Not Found**:
    ```json
    {
      "error": "Tipe kamar aktif 'presidential' tidak ditemukan"
    }
    ```
  - **409 Conflict**:
    ```json
    {
      "error": "Tidak dapat menonaktifkan tipe kamar karena ada booking aktif",
      "active_bookings_count": 2,
      "detail": "Ada booking yang belum selesai (check-out di masa depan)"
    }
    ```
  - **503 Service Unavailable**:
    ```json
    {
      "error": "Tidak dapat terhubung ke BookingService",
      "details": "Connection timed out"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Gagal menonaktifkan tipe kamar",
      "details": "Database connection error"
    }
    ```

### Update Room Type

- **Endpoint**: `PUT /rooms/{type_code}`
- **Port**: 5003
- **Validasi Path Parameter**:

  - `type_code`: Wajib diisi, harus ada dalam database dan statusnya aktif

- **Request Body**:

```json
{
    "name": "string" (optional),
    "description": "string" (optional),
    "price_per_night": number (optional)
}
```

- **Validasi Input**:

  - Request body tidak boleh kosong
  - `price_per_night`: Jika diisi, harus angka positif

- **Success Response** (200):

```json
[
  {
    "status": "ok",
    "message": "Kamar deluxe berhasil diperbaharui."
  },
  {
    "type_code": "deluxe",
    "name": "Deluxe Room Updated",
    "description": "Kamar mewah dengan pemandangan kota",
    "price_per_night": 850000,
    "is_active": true
  }
]
```

- **Error Responses**:
  - **400 Bad Request**:
    ```json
    {
      "error": "Request body tidak boleh kosong"
    }
    ```
  - **400 Bad Request** (Harga tidak valid):
    ```json
    {
      "error": "Nilai price_per_night tidak valid atau tidak positif"
    }
    ```
  - **404 Not Found**:
    ```json
    {
      "error": "Tipe kamar aktif 'presidential' tidak ditemukan"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Gagal memperbarui tipe kamar",
      "details": "[pesan error database]"
    }
    ```

## Payment Service

### Create Payment

- **Endpoint**: `POST /payments`
- **Request Body**:

```json
{
    "booking_uid": "string",
    "amount": number
}
```

- **Validasi Input**:

  - Semua field wajib diisi
  - `booking_uid`: Harus ada di Booking Service dan statusnya 'pending_payment'
  - `amount`: Harus angka positif dan sesuai dengan total_price di booking

- **Success Response** (200):

```json
{
  "payment_uid": "string",
  "booking_uid": "string",
  "requested_amount": 800000,
  "status": "success",
  "message": "Pembayaran berhasil diproses",
  "failure_reason": null,
  "request_time": "2023-12-20T10:00:00Z",
  "processed_at": "2023-12-20T10:00:02Z",
  "is_fraud": false,
  "fraud_score": 0.15
}
```

- **Error Responses**:
  - **400 Bad Request** (Data tidak lengkap):
    ```json
    {
      "error": "Data tidak lengkap (booking_uid, amount)"
    }
    ```
  - **400 Bad Request** (Jumlah tidak valid):
    ```json
    {
      "error": "Nilai 'amount' tidak valid atau tidak positif"
    }
    ```
  - **400 Bad Request** (Status booking tidak valid):
    ```json
    {
      "error": "Booking B12345 tidak dalam status 'pending_payment' (status saat ini: confirmed)"
    }
    ```
  - **400 Bad Request** (Jumlah tidak sesuai):
    ```json
    {
      "error": "Jumlah pembayaran (750000) tidak sesuai dengan tagihan booking (800000)"
    }
    ```
  - **503 Service Unavailable** (Layanan booking tidak tersedia):
    ```json
    {
      "error": "Gagal menghubungi Booking Service",
      "details": "[pesan error]"
    }
    ```
  - **503 Service Unavailable** (Layanan tamu tidak tersedia):
    ```json
    {
      "error": "Gagal menghubungi Guest Service",
      "details": "[pesan error]"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Gagal memulai transaksi pembayaran",
      "details": "[pesan error database]"
    }
    ```

### Get Payment Status

- **Endpoint**: `GET /payments/{payment_uid}`
- **Validasi Path Parameter**:

  - `payment_uid`: Wajib diisi, harus ada dalam database

- **Success Response** (200):

```json
{
  "payment_uid": "string",
  "booking_uid": "string",
  "requested_amount": 800000,
  "status": "success",
  "message": "Pembayaran berhasil diproses",
  "failure_reason": null,
  "request_time": "2023-12-20T10:00:00Z",
  "processed_at": "2023-12-20T10:00:02Z",
  "is_fraud": false,
  "fraud_score": 0.15
}
```

- **Error Responses**:
  - **404 Not Found**:
    ```json
    {
      "error": "Transaksi pembayaran tidak ditemukan"
    }
    ```
  - **500 Internal Server Error**:
    ```json
    {
      "error": "Kesalahan database",
      "details": "[pesan error database]"
    }
    ```

### Get All Payments

- **Endpoint**: `GET /payments`
- **Query Parameters**:

  - `booking_uid` (optional): Filter transaksi berdasarkan booking
  - `status` (optional): Filter transaksi berdasarkan status

- **Success Response** (200):
  Success Response (200):

```json
    {
        "payment_uid": "pay_abc123",
        "booking_uid": "book_123",
        "requested_amount": 800000,
        "status": "success",
        "message": "Pembayaran berhasil diproses",
        "request_time": "2023-12-20T10:00:00Z",
        "processed_at": "2023-12-20T10:00:02Z",
        "is_fraud": false,
        "fraud_score": 0.15
    },
    {
        "payment_uid": "pay_def456",
        "booking_uid": "book_456",
        "requested_amount": 1200000,
        "status": "failed",
        "message": "Pembayaran gagal: CARD_DECLINED",
        "failure_reason": "CARD_DECLINED",
        "request_time": "2023-12-19T15:30:00Z",
        "processed_at": "2023-12-19T15:30:45Z",
        "is_fraud": false,
        "fraud_score": 0.05
    }
```

- **Error Responses**:
- **500 Internal Server Error**:

```json
{
  "error": "Kesalahan database",
  "details": "[pesan error database]"
}
```

### Get Fraud Analysis Report

- **Endpoint**: GET /payments/fraud-analysis
- **Success Response (200)**:

```json
{
  "total_transactions": 150,
  "total_success_transactions": 120,
  "total_fraud_detected": 8,
  "fraud_percentage": 6.67,
  "fraud_transactions": [
    {
      "payment_uid": "pay_xyz789",
      "booking_uid": "book_789",
      "requested_amount": 4500000,
      "status": "failed",
      "message": "Pembayaran ditolak: TERDETEKSI FRAUD",
      "failure_reason": "FRAUD_DETECTION",
      "request_time": "2023-12-18T02:15:00Z",
      "processed_at": "2023-12-18T02:15:05Z",
      "is_fraud": true,
      "fraud_score": 0.92
    }
  ]
}
```

- **Error Respons**:
  500 Internal Server Error:

```json
{
  "error": "Gagal mendapatkan analisis fraud",
  "details": "Internal server error"
}
```

## analisis pembayaran fraud
**Endpoint**: GET /payments/{payment_uid}/analyze-fraud

Success Response (200):

```json
{
  "payment_uid": "pay_xyz789",
  "transaction": {
    "payment_uid": "pay_xyz789",
    "booking_uid": "book_789",
    "requested_amount": 4500000,
    "status": "failed",
    "message": "Pembayaran ditolak: TERDETEKSI FRAUD",
    "failure_reason": "FRAUD_DETECTION",
    "request_time": "2023-12-18T02:15:00Z",
    "processed_at": "2023-12-18T02:15:05Z",
    "is_fraud": true,
    "fraud_score": 0.92
  },
  "fraud_analysis": {
    "is_fraud": true,
    "fraud_score": 0.92,
    "fraud_threshold": 0.7,
    "high_risk_threshold": 0.85,
    "features": [
      { "name": "Jumlah (Rp)", "value": 4500000 },
      { "name": "Waktu Proses (detik)", "value": 5 },
      { "name": "Waktu Hari (jam)", "value": 2.25 },
      { "name": "Hari Minggu (0-6)", "value": 6 },
      { "name": "Durasi Booking (hari)", "value": 10 },
      { "name": "Hari Sebelum Check-in", "value": 3 }
    ],
    "feature_importance": [
      {
        "name": "Jumlah (Rp)",
        "value": 4500000,
        "importance": 0.35,
        "contribution": 1575000
      }
    ],
    "risk_level": "Tinggi"
  }
}
```

- **404 Not Found**:

```json
{
  "error": "Transaksi pembayaran tidak ditemukan"
}
```

- **500 Internal Server Error**:

```json
{
  "error": "Gagal menganalisis fraud",
  "details": "Internal server error"
}
```

# Sistem Manajemen Hotel - Fraud Detection

Sistem ini adalah aplikasi manajemen hotel dengan fitur machine learning untuk mendeteksi transaksi pembayaran yang berpotensi fraud.

## Fitur Deteksi Fraud

Fitur machine learning untuk mendeteksi transaksi pembayaran yang mencurigakan dengan karakteristik:

- **Model**: Random Forest Classifier
- **Training**: Menggunakan data dummy
- **Fitur yang digunakan**:
  - Jumlah pembayaran
  - Waktu pemrosesan transaksi
  - Waktu transaksi (jam dalam hari)
  - Hari dalam minggu
  - Durasi booking
  - Hari sebelum check-in

### Pola Fraud yang Dideteksi

Model dilatih untuk mendeteksi pola-pola fraud seperti:

1. Transaksi dengan jumlah sangat besar (> 4 juta) dan proses cepat (< 60 detik)
2. Transaksi tengah malam (jam 0-4) dengan durasi booking panjang (> 7 hari)
3. Transaksi hari Minggu dengan jumlah besar

### Proses Deteksi Fraud

1. Setiap transaksi pembayaran diperiksa secara real-time oleh model ML
2. Model menghasilkan skor fraud (0-1) dan flag (true/false)
3. Transaksi dengan skor fraud > 0.85 ditolak otomatis
4. Transaksi dengan skor fraud > 0.7 ditandai sebagai mencurigakan

### Tampilan Analisis Fraud

Sistem menyediakan tampilan dan dashboard untuk:

1. Halaman Analisis Fraud\*\*: Menampilkan ringkasan dan statistik semua transaksi fraud
2. Detail Analisis Fraud\*\*: Menampilkan detail analisis fraud per transaksi
3. Integrasi di halaman Pembayaran\*\*: Indikator visual dan tombol untuk transaksi mencurigakan
