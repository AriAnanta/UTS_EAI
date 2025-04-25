from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import requests
import os
import datetime


app = Flask(__name__)

@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}

MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_DB = os.environ.get('MYSQL_GUEST_DB', 'guest_db')
MYSQL_PORT = os.environ.get('MYSQL_PORT', '3308') 
DB_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Model Database ---
class Guest(db.Model):
    __tablename__ = 'guests'
    id = db.Column(db.Integer, primary_key=True)
    guest_uid = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True) # Untuk melakukan Soft Delete

    def to_dict(self):
        return {
            "guest_uid": self.guest_uid,
            "name": self.name,
            "email": self.email,
            "phone": self.phone
        }

# URL BookingService dari environment variable atau gunakan default(File .env-nya)
BOOKING_SERVICE_URL = os.environ.get('BOOKING_SERVICE_URL', 'http://127.0.0.1:5002')

# Membuat data tamu baru
@app.route('/guests', methods=['POST'])
def create_guest():
    """Membuat data tamu baru. Memastikan tidak ada duplikat UID/Email aktif."""
    data = request.get_json()
    if not data or not data.get('guest_uid') or not data.get('name') or not data.get('email'):
         return jsonify({"error": "Data tidak lengkap (membutuhkan guest_uid, name, email)"}), 400
    try:
        if Guest.query.filter_by(guest_uid=data['guest_uid'], is_deleted=False).first():
            return jsonify({"error": f"Guest UID '{data['guest_uid']}' aktif sudah ada"}), 409
        if Guest.query.filter_by(email=data['email'], is_deleted=False).first():
            return jsonify({"error": f"Email '{data['email']}' aktif sudah terdaftar"}), 409

        new_guest = Guest(
            guest_uid=data['guest_uid'], name=data['name'],
            email=data['email'], phone=data.get('phone'),
            is_deleted=False 
        )
        db.session.add(new_guest)
        db.session.commit()
        print(f"Tamu baru dibuat: {new_guest.guest_uid}")
        
        response = {
            "message": "Data tamu berhasil dibuat",
            "guest": new_guest.to_dict()
        }
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error buat data tamu baru: {e}")
        return jsonify({"error": "Gagal menyimpan data tamu", "details": str(e)}), 500

# Mengambil semua data tamu
@app.route('/guests', methods=['GET'])
def get_all_guests():
    """Mendapatkan daftar semua tamu yang aktif (belum dihapus)."""
    try:
        # Filter hanya tamu yang belum dihapus dimaan kolom is_delete itu False
        guests = Guest.query.filter_by(is_deleted=False).order_by(Guest.name).all()
        return jsonify([g.to_dict() for g in guests])
    except Exception as e:
        print(f"Error ketika mencoba ambil data semua tamu: {e}")
        return jsonify({"error": "Kesalahan database saat mengambil daftar tamu", "details": str(e)}), 500

# Ambil data tamu berdasarkan guest_uid
@app.route('/guests/<guest_uid>', methods=['GET'])
def get_guest(guest_uid):
    """Mendapatkan detail tamu aktif berdasarkan guest_uid."""
    try:
        guest = Guest.query.filter_by(guest_uid=guest_uid, is_deleted=False).first()
        if guest:
            return jsonify(guest.to_dict())
        else:
            return jsonify({"error": "Tamu aktif tidak ditemukan"}), 404
    except Exception as e:
        print(f"Error ketika ambil data tamu: {e}")
        return jsonify({"error": "Kesalahan database saat mengambil data tamu", "details": str(e)}), 500

# update data tamu tapi hanya yang aktif aja
@app.route('/guests/<guest_uid>', methods=['PUT'])
def update_guest(guest_uid):
    """Memperbarui data tamu aktif."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body tidak boleh kosong"}), 400

    try:
        # Hanya update tamu yang aktif
        guest = Guest.query.filter_by(guest_uid=guest_uid, is_deleted=False).first()
        if not guest:
            return jsonify({"error": "Tamu aktif tidak ditemukan untuk diperbarui"}), 404

        # Validasi email unik jika diubah
        new_email = data.get('email')
        if new_email and new_email != guest.email:
            if Guest.query.filter(Guest.email == new_email, Guest.guest_uid != guest_uid, Guest.is_deleted == False).first():
                 return jsonify({"error": f"Email '{new_email}' sudah digunakan tamu aktif lain"}), 409
            guest.email = new_email

        if 'name' in data: guest.name = data['name']
        if 'phone' in data: guest.phone = data['phone']

        db.session.commit()
        print(f"Data tamu {guest_uid} diperbarui.")
        respon = {'message': 'Data tamu berhasil diperbarui',
                  'guest': guest.to_dict()}
        return jsonify(respon), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error ketika update data tamu: {e}")
        return jsonify({"error": "Gagal memperbarui data tamu", "details": str(e)}), 500

# Hapus data tamu dengan soft delete  
@app.route('/guests/<guest_uid>', methods=['DELETE'])
def delete_guest(guest_uid):
    """Menandai tamu sebagai dihapus (Soft Delete)."""
    try:
        guest = Guest.query.filter_by(guest_uid=guest_uid, is_deleted=False).first()
        if not guest:
            return jsonify({"error": "Tamu aktif tidak ditemukan untuk dihapus"}), 404

        # Cek booking aktif mendatang untuk mencegah penghapusan tamu yang akan check-in
        try:
            # Cek booking dengan status confirmed 
            booking_check_url = f"{BOOKING_SERVICE_URL}/bookings?guest_uid={guest_uid}&status=confirmed"
            response = requests.get(booking_check_url, timeout=5)
            
            if response.ok:
                bookings = response.json()
                # Filter booking yang check-in-nya di masa depan
                today = datetime.date.today().isoformat()
                future_bookings = [b for b in bookings if b.get('check_in_date', '') > today]
                
                if future_bookings:
                    return jsonify({
                        "error": "Tidak dapat menghapus tamu karena memiliki booking aktif mendatang",
                        "booking_count": len(future_bookings)
                    }), 409
        except requests.exceptions.RequestException as e:
            print(f"Warning: Gagal memeriksa booking saat delete guest: {e}")

        # Lakukan Soft Delete
        guest.is_deleted = True
        db.session.commit()
        print(f"Data tamu {guest_uid} ditandai sebagai dihapus (soft delete).")
        return jsonify({'message': 'Data tamu berhasil dihapus'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error ketika hapus data tamu: {e}")
        return jsonify({"error": "Gagal menghapus data tamu", "details": str(e)}), 500


# Route untuk mengambildata booking yg dimiliki oleh tamu
@app.route('/guests/<guest_uid>/bookings', methods=['GET'])
def get_guest_bookings(guest_uid):
    """Mendapatkan riwayat pemesanan tamu (memanggil BookingService)."""
    try:
        guest = Guest.query.filter_by(guest_uid=guest_uid, is_deleted=False).first()
        if not guest:
            # Tamu tidak aktif atau tidak ada
            return jsonify({"error": "Tamu aktif tidak ditemukan"}), 404
    except Exception as e:
         print(f"Error ketika verifikasi data booking tamu: {e}")
         return jsonify({"error": "Kesalahan database saat verifikasi tamu"}), 500

    # Panggil BookingService
    try:
        booking_service_endpoint = f"{BOOKING_SERVICE_URL}/bookings?guest_uid={guest_uid}"
        response = requests.get(booking_service_endpoint, timeout=5)
        response.raise_for_status() 
        bookings = response.json()
        return jsonify(bookings)
    except requests.exceptions.Timeout:
         return jsonify({"error": "Timeout saat menghubungi BookingService"}), 504 
    except requests.exceptions.RequestException as e:
        status_code = 503 
        if e.response is not None:
             status_code = e.response.status_code 
        print(f"Error calling BookingService: {e}")
        return jsonify({"error": "Tidak dapat mengambil data pemesanan dari BookingService", "details": str(e)}), status_code
    except Exception as e:
        print(f"Ada error ketika mengambil data booking: {e}")
        return jsonify({"error": "Terjadi kesalahan tak terduga saat mengambil booking"}), 500

if __name__ == '__main__':
    with app.app_context():
        print(f"Mencoba terhubung ke database: {DB_URI}")
        try: db.engine.connect(); print("Koneksi Database berhasil terhubung"); db.create_all(); print("Tabel sudah ada.")
        except Exception as e: print(f"GAGAL KONEKSI DB: {e}"); import sys; sys.exit(1)
    print("Guest service jalaan di port 5001 Euy")
    app.run(host='0.0.0.0', port=5001, debug=True)

