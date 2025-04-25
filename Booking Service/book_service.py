# booking_service.py
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import requests
import os
import uuid
import datetime

app = Flask(__name__)

@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}

# --- Konfigurasi Database MySQL ---
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_DB = os.environ.get('MYSQL_BOOKING_DB', 'booking_db') 
MYSQL_PORT = os.environ.get('MYSQL_PORT', '3308') 
DB_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Model Database ---
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    booking_uid = db.Column(db.String(80), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    guest_uid = db.Column(db.String(80), nullable=False, index=True)
    room_type_code = db.Column(db.String(50), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), nullable=False, default='pending_payment', index=True)
    payment_id = db.Column(db.String(100), nullable=True)
    booking_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    cancellation_reason = db.Column(db.Text, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)


    def to_dict(self):
        data = { "booking_uid": self.booking_uid, 
                "guest_uid": self.guest_uid, 
                "room_type_code": self.room_type_code, 
                "check_in_date": self.check_in_date.isoformat(), 
                "check_out_date": self.check_out_date.isoformat(), 
                "total_price": self.total_price, "status": self.status, 
                "payment_id": self.payment_id, 
                "booking_time": self.booking_time.isoformat() + "Z" }
        if self.status == 'cancelled':
            data['cancellation_reason'] = self.cancellation_reason
            if self.cancelled_at:
                 data['cancelled_at'] = self.cancelled_at.isoformat() + "Z"
        return data
    
# Dapatkan URL service lain dari environment variables
GUEST_SERVICE_URL = os.environ.get('GUEST_SERVICE_URL', 'http://127.0.0.1:5001')
ROOM_SERVICE_URL = os.environ.get('ROOM_SERVICE_URL', 'http://127.0.0.1:5003')
PAYMENT_SERVICE_URL = os.environ.get('PAYMENT_SERVICE_URL', 'http://127.0.0.1:5004')

def validate_guest(guest_uid):
    """Memvalidasi guest_uid DAN memastikan tamu aktif."""
    try:
        # GuestService GET /guests/{uid} sudah otomatis filter tamu aktif
        response = requests.get(f"{GUEST_SERVICE_URL}/guests/{guest_uid}", timeout=5)
        if response.ok: return True, response.json() # Tamu valid dan aktif
        elif response.status_code == 404: return False, {"error": "Tamu tidak ditemukan atau tidak aktif"}
        else: response.raise_for_status(); return False, {"error": f"GuestService error {response.status_code}"}
    except requests.exceptions.Timeout: return False, {"error": "Timeout hubungi GuestService"}
    except requests.RequestException as e: return False, {"error": "Gagal hubungi GuestService", "details": str(e)}
    except Exception as e: return False, {"error": f"Error validasi tamu: {e}"}

def get_room_details(room_type_code):
    """Mendapatkan detail kamar DAN memastikan tipe kamar aktif."""
    try:
        # RoomService GET /rooms/{code} sudah otomatis filter tipe aktif
        response = requests.get(f"{ROOM_SERVICE_URL}/rooms/{room_type_code}", timeout=5)
        if response.ok: return True, response.json() 
        elif response.status_code == 404: return False, {"error": f"Tipe kamar '{room_type_code}' tidak ditemukan atau tidak aktif"}
        else: response.raise_for_status(); return False, {"error": f"RoomService error {response.status_code}"}
    except requests.exceptions.Timeout: return False, {"error": "Timeout hubungi RoomService"}
    except requests.RequestException as e: return False, {"error": "Gagal hubungi RoomService", "details": str(e)}
    except Exception as e: return False, {"error": f"Error ambil detail kamar: {e}"}

def trigger_payment(booking_uid, amount): 
    try: payload = {"booking_uid": booking_uid, "amount": amount}; response = requests.post(f"{PAYMENT_SERVICE_URL}/payments", json=payload, timeout=10); response.raise_for_status(); return True, response.json()
    except requests.exceptions.Timeout: return False, {"error": "Timeout hubungi PaymentService"}
    except requests.RequestException as e: return False, {"error": "Gagal hubungi PaymentService", "details": str(e)}
    except Exception as e: return False, {"error": f"Error picu pembayaran: {e}"}

# Membuat data booking baru dimana status pemesanan adalah 'pending_payment'
@app.route('/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()
    required_fields = ['guest_uid', 'room_type_code', 'check_in', 'check_out']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": f"Data tidak lengkap ({', '.join(required_fields)})"}), 400

    guest_uid = data['guest_uid']
    room_type_code = data['room_type_code'].lower()
    check_in_str, check_out_str = data['check_in'], data['check_out']

    # 1. Validasi Tamu Aktif
    guest_valid, guest_info = validate_guest(guest_uid)
    if not guest_valid:
        status_code = 503 if "Gagal hubungi" in guest_info.get("error", "") else 400
        return jsonify(guest_info), status_code 

    # 2. Validasi Tipe Kamar Aktif
    room_valid, room_info = get_room_details(room_type_code)
    if not room_valid:
        status_code = 503 if "Gagal hubungi" in room_info.get("error", "") else 404
        return jsonify(room_info), status_code
    price_per_night = room_info.get('price_per_night')
    if price_per_night is None:
         return jsonify({"error": "Data harga tidak ditemukan dari RoomService"}), 500

    # 3. Validasi Tanggal
    try:
        check_in_date = datetime.date.fromisoformat(check_in_str)
        check_out_date = datetime.date.fromisoformat(check_out_str)
        # Cek tanggal valid & tidak di masa lalu
        if check_out_date <= check_in_date or check_in_date < datetime.date.today():
            return jsonify({"error": "Tanggal check-in/check-out tidak valid"}), 400
    except ValueError:
        return jsonify({"error": "Format tanggal tidak valid (YYYY-MM-DD)"}), 400

    # 5. Hitung Harga
    num_nights = (check_out_date - check_in_date).days
    total_price = num_nights * price_per_night

    # 6. Buat Booking Awal
    new_booking = Booking(
        guest_uid=guest_uid, room_type_code=room_type_code,
        check_in_date=check_in_date, check_out_date=check_out_date,
        total_price=total_price, status='pending_payment'
    )
    try:
        db.session.add(new_booking)
        db.session.commit()
        print(f"Booking {new_booking.booking_uid} dibuat, status: pending_payment.")
    except Exception as e:
        db.session.rollback(); print(f"Darabase error ketika buat data booking: {e}")
        return jsonify({"error": "Gagal menyimpan data pemesanan", "details": str(e)}), 500
    try:
        # Pastikan booking masih ada di database
        booking_to_return = Booking.query.filter_by(booking_uid=new_booking.booking_uid).first()
        if not booking_to_return:
            print(f"CRITICAL: Booking {new_booking.booking_uid} hilang setelah dibuat!")
            return jsonify({"error": "Booking hilang setelah dibuat"}), 500
            
        print(f"Booking {new_booking.booking_uid} berhasil dibuat dengan status: pending_payment.")
        return jsonify(booking_to_return.to_dict()), 201

    except Exception as e:
        db.session.rollback(); print(f"Error ketika mengambil data booking: {e}")
        return jsonify({"error": "Booking dibuat, tetapi gagal mengambil data booking", "details": str(e)}), 500

# Ambil semuda data booking
@app.route('/bookings', methods=['GET'])
def get_all_or_by_guest(): 
    guest_uid_filter = request.args.get('guest_uid')
    status_filter = request.args.get('status')
    try:
        query = Booking.query
        if guest_uid_filter: query = query.filter(Booking.guest_uid == guest_uid_filter)
        if status_filter: query = query.filter(Booking.status == status_filter)
        bookings = query.order_by(Booking.booking_time.desc()).all()
        return jsonify([b.to_dict() for b in bookings])
    except Exception as e: print(f"DB error get_bookings: {e}"); return jsonify({"error": "Kesalahan DB", "details": str(e)}), 500

# Ambil booking berdasarkan booking_uid
@app.route('/bookings/<booking_uid>', methods=['GET'])
def get_booking(booking_uid): 
    try: booking = Booking.query.filter_by(booking_uid=booking_uid).first(); return jsonify(booking.to_dict()) if booking else (jsonify({"error": "Tidak ditemukan"}), 404)
    except Exception as e: print(f"databse error: {e}"); return jsonify({"error": "Kesalahan DB", "details": str(e)}), 500

@app.route('/bookings/<booking_uid>/confirm-payment', methods=['PUT'])
def confirm_booking_payment(booking_uid):
    data = request.get_json()
    if not data or not data.get('payment_uid'):
        return jsonify({"error": "Data payment_uid diperlukan"}), 400

    try:
        booking = Booking.query.filter_by(booking_uid=booking_uid).first()
        if not booking:
            return jsonify({"error": "Booking tidak ditemukan"}), 404

        # Update status dan payment_id
        booking.status = 'confirmed'
        booking.payment_id = data['payment_uid']
        
        db.session.commit()
        
        return jsonify({
            "message": "Booking berhasil dikonfirmasi",
            "booking": booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saat konfirmasi pembayaran booking: {str(e)}")
        return jsonify({
            "error": "Gagal mengkonfirmasi pembayaran booking",
            "details": str(e)
        }), 500

@app.route('/bookings/by-room', methods=['GET'])
def get_bookings_by_room_type():
    """
    Mengambil daftar booking berdasarkan room_type_code"""
    
    room_type_filter = request.args.get('room_type_code')
    status_filter = request.args.get('status')

    if not room_type_filter:
        return jsonify({"error": "Parameter room_type_code wajib disertakan"}), 400

    try:
        query = Booking.query.filter(Booking.room_type_code == room_type_filter.lower())
        if status_filter:
            query = query.filter(Booking.status == status_filter)

        bookings = query.order_by(Booking.booking_time.desc()).all()
        return jsonify([b.to_dict() for b in bookings]), 200
    except Exception as e:
        print(f"DB error in get_bookings_by_room_type: {e}")
        return jsonify({"error": "Kesalahan DB", "details": str(e)}), 500


# UPDATE status booking
@app.route('/bookings/<booking_uid>/cancel', methods=['PUT'])
def cancel_booking(booking_uid):
    """Membatalkan pemesanan dengan validasi kebijakan."""
    data = request.get_json() 
    reason = data.get('reason', 'Dibatalkan oleh pengguna') if data else 'Dibatalkan oleh pengguna'

    try:
        booking = Booking.query.filter_by(booking_uid=booking_uid).first()
        if not booking:
            return jsonify({"error": "Pemesanan tidak ditemukan"}), 404

        # 1. Cek Status Saat Ini
        cancellable_statuses = ['confirmed', 'pending_payment']
        if booking.status not in cancellable_statuses:
             return jsonify({"error": f"Booking dengan status '{booking.status}' tidak dapat dibatalkan"}), 409

        # 2. Cek Kebijakan Pembatalan (Contoh: Tidak bisa batal H-1 check-in)
        cancellation_deadline = booking.check_in_date - datetime.timedelta(days=1)
        if datetime.date.today() >= cancellation_deadline:
            return jsonify({"error": f"Pembatalan tidak diizinkan setelah atau pada {cancellation_deadline.isoformat()} (H-1 check-in)"}), 400

        # 3. Melakukan Cancel pada booking
        booking.status = 'cancelled'
        booking.cancellation_reason = reason
        booking.cancelled_at = datetime.datetime.utcnow()

        db.session.commit()
        print(f"Booking {booking_uid} dibatalkan. Alasan: {reason}")
        return jsonify(booking.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Database error in cancel_booking: {e}")
        return jsonify({"error": "Gagal membatalkan booking", "details": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        print(f"Mencoba terhubung ke database: {DB_URI}")
        try: db.engine.connect(); print("Koneksi database berhasil"); db.create_all(); print("Tabel siap.")
        except Exception as e: print(f"Gagal koneksi database: {e}"); import sys; sys.exit(1)
    print("Starting BookingService jalan di port 5002 EuY")
    app.run(host='0.0.0.0', port=5002, debug=True)