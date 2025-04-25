# room_service.py
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import requests
import datetime

app = Flask(__name__)

@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}

# --- Konfigurasi Database MySQL ---
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_DB = os.environ.get('MYSQL_ROOM_DB', 'room_db') 
MYSQL_PORT = os.environ.get('MYSQL_PORT', '3308') 
DB_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Model Database ---
class RoomType(db.Model):
    __tablename__ = 'room_types'
    id = db.Column(db.Integer, primary_key=True)
    type_code = db.Column(db.String(50), unique=True, nullable=False) 
    name = db.Column(db.String(100), nullable=False) 
    description = db.Column(db.Text, nullable=True)
    price_per_night = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
   
    def to_dict(self):
        return {
            "type_code": self.type_code,
            "name": self.name,
            "description": self.description,
            "price_per_night": self.price_per_night
        }

# Buat data kamar yang baru
@app.route('/rooms', methods=['POST'])
def add_room_type():
    data = request.get_json()
    required = ['type_code', 'name', 'price_per_night']
    if not data or not all(field in data for field in required):
        return jsonify({"error": f"Data tidak lengkap ({', '.join(required)})"}), 400

    type_code = data['type_code'].lower()

    try:
        # Cek duplikat pada tipe kamar yang aktif
        if RoomType.query.filter_by(type_code=type_code, is_active=True).first():
            return jsonify({"error": f"Tipe kamar aktif dengan kode '{type_code}' sudah ada"}), 409

        new_room_type = RoomType(
            type_code=type_code, name=data['name'],
            price_per_night=data['price_per_night'], description=data.get('description'),
            is_active=True # Tipe kamar baru selalu di set aktif
        )
        respon = {'status': 'ok', 'message': f'Kamar {type_code} berhasil ditambahkan.'}
        db.session.add(new_room_type)
        db.session.commit()
        print(f"Tipe kamar baru ditambahkan: {type_code}")
        return jsonify(respon, new_room_type.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error gagal menambahakan data baru kamar: {e}")
        return jsonify({"error": "Gagal menyimpan tipe kamar", "details": str(e)}), 500

# Baca semua data kamar tapi yang aktid aja
@app.route('/rooms', methods=['GET'])
def get_all_room_types():
    try:
        # Filter hanya yang aktif
        room_types = RoomType.query.filter_by(is_active=True).order_by(RoomType.name).all()
        return jsonify([rt.to_dict() for rt in room_types])
    except Exception as e:
        print(f"Error saat mengambil data kamar: {e}")
        return jsonify({"error": "Kesalahan database saat mengambil tipe kamar", "details": str(e)}), 500

# Baca data kamar berdsarkan type code nya aja
@app.route('/rooms/<type_code>', methods=['GET'])
def get_room_type_details(type_code):
    try:
        # Cari yang spesifik DAN aktif
        room_type = RoomType.query.filter_by(type_code=type_code.lower(), is_active=True).first()
        if room_type:
            return jsonify(room_type.to_dict())
        else:
            return jsonify({"error": f"Tipe kamar aktif '{type_code}' tidak ditemukan"}), 404
    except Exception as e:
        print(f"Error mengambil data detail kamar: {e}")
        return jsonify({"error": "Kesalahan database saat mengambil detail kamar", "details": str(e)}), 500

# Update data kamar
@app.route('/rooms/<type_code>', methods=['PUT'])
def update_room_type(type_code):
    """Memperbarui detail tipe kamar aktif."""
    data = request.get_json()
    if not data:
         return jsonify({"error": "Request body tidak boleh kosong"}), 400

    try:
        # Hanya update tipe kamar yang aktif aja
        room_type = RoomType.query.filter_by(type_code=type_code.lower(), is_active=True).first()
        if not room_type:
            return jsonify({"error": f"Tipe kamar aktif '{type_code}' tidak ditemukan"}), 404

        if 'name' in data: room_type.name = data['name']
        if 'description' in data: room_type.description = data['description']
        if 'price_per_night' in data:
            try:
                price = float(data['price_per_night'])
                if price <= 0: raise ValueError("Harga harus positif") # Validasi harga > 0
                room_type.price_per_night = price
            except (ValueError, TypeError):
                 return jsonify({"error": "Nilai price_per_night tidak valid atau tidak positif"}), 400
        respon = {'status': 'ok', 'message': f'Kamar {type_code} berhasil diperbaharui.'}
        db.session.commit()
        print(f"Tipe kamar {type_code} diperbarui.")
        return jsonify(respon, room_type.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error memperbaharui data kamar: {e}")
        return jsonify({"error": "Gagal memperbarui tipe kamar", "details": str(e)}), 500

# Delete data kamar dengan soft delete
@app.route('/rooms/<type_code>', methods=['DELETE'])
def delete_room_type(type_code):
    """Menonaktifkan tipe kamar (Soft Delete) dengan validasi booking aktif."""
    try:
        # Cari kamar yang aktif
        room_type = RoomType.query.filter_by(type_code=type_code.lower(), is_active=True).first()
        if not room_type:
            return jsonify({"error": f"Tipe kamar aktif '{type_code}' tidak ditemukan"}), 404
        try:
            # Panggil BookingService untuk mendapatkan semua booking untuk tipe kamar ini
            booking_check_url = f"{BOOKING_SERVICE_URL}/bookings/by-room?room_type_code={type_code}"
            response = requests.get(booking_check_url, timeout=10)
            
            if response.ok:
                bookings = response.json()
                print(f"Data booking diterima: {bookings}")  
                
                if bookings:  
                    today = datetime.date.today()
                    active_bookings = []
                    
                    for booking in bookings:
                        if booking.get('status', '').lower() == 'cancelled':
                            continue
                            
                        try:
                            check_out_date = datetime.date.fromisoformat(booking.get('check_out_date'))
                        except (ValueError, TypeError):
                            continue
                            
                        # Jika check_out_date masih di masa depan, berarti booking masih aktif
                        if check_out_date >= today:
                            active_bookings.append(booking)
                    
                    print(f"Booking aktif ditemukan: {len(active_bookings)}")  
                    
                    if active_bookings:
                        return jsonify({
                            "error": "Tidak dapat menonaktifkan tipe kamar karena ada booking aktif",
                            "active_bookings_count": len(active_bookings),
                            "detail": "Ada booking yang belum selesai (check-out di masa depan)"
                        }), 409
            else:
                print(f"Response dari BookingService tidak OK: {response.status_code}")
                return jsonify({
                    "error": "Gagal memverifikasi booking",
                    "details": f"BookingService returned {response.status_code}"
                }), 503

        except requests.exceptions.RequestException as e:
            print(f"Error saat memeriksa booking: {str(e)}")
            return jsonify({
                "error": "Tidak dapat terhubung ke BookingService",
                "details": str(e)
            }), 503

        room_type.is_active = False
        db.session.commit()
        
        return jsonify({
            "message": f"Tipe kamar {type_code} berhasil dinonaktifkan",
            "room_type": room_type.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saat menghapus kamar: {str(e)}")
        return jsonify({
            "error": "Gagal menonaktifkan tipe kamar",
            "details": str(e)
        }), 500

@app.route('/rooms/<type_code>/availability', methods=['GET'])
def check_room_availability(type_code):
    """Endpoint cek ketersediaan kamar dengan validasi booking yang ada."""
    check_in_str = request.args.get('check_in')
    check_out_str = request.args.get('check_out')
    
    # Validasi parameter tanggal
    if not check_in_str or not check_out_str:
        return jsonify({"error": "Parameter check_in dan check_out diperlukan"}), 400
    
    try:
        # Validasi format tanggal
        try:
            check_in_date = datetime.date.fromisoformat(check_in_str)
            check_out_date = datetime.date.fromisoformat(check_out_str)
            if check_out_date <= check_in_date:
                return jsonify({"error": "check_out harus setelah check_in"}), 400
        except ValueError:
            return jsonify({"error": "Format tanggal tidak valid (YYYY-MM-DD)"}), 400
        
        # Cek apakah tipe kamar ada DAN aktif
        room_type = RoomType.query.filter_by(type_code=type_code.lower(), is_active=True).first()
        if not room_type:
            return jsonify({"type_code": type_code, "available": False, "message": "Tipe kamar tidak aktif atau tidak ditemukan"}), 404
        
        try:
            MAX_ROOMS_PER_TYPE = 5  # Pakai 5 sebagai asumsi maksimal jumlah kamar per tipe
            
            # Panggil BookingService untuk mendapatkan booking yang ada
            booking_check_url = f"{BOOKING_SERVICE_URL}/bookings?room_type_code={type_code}&status=confirmed"
            response = requests.get(booking_check_url, timeout=5)
            
            if response.ok:
                bookings = response.json()
                # Filter booking yang overlap dengan tanggal yang diminta
                overlapping_bookings = []
                for booking in bookings:
                    booking_check_in = datetime.date.fromisoformat(booking.get('check_in_date'))
                    booking_check_out = datetime.date.fromisoformat(booking.get('check_out_date'))
                    
                    # Cek apakah ada overlap
                    if (check_in_date < booking_check_out and check_out_date > booking_check_in):
                        overlapping_bookings.append(booking)
                
                # Hitung ketersediaan
                booked_count = len(overlapping_bookings)
                available_count = MAX_ROOMS_PER_TYPE - booked_count
                is_available = available_count > 0
                
                return jsonify({
                    "type_code": type_code,
                    "available": is_available,
                    "available_count": available_count,
                    "total_rooms": MAX_ROOMS_PER_TYPE,
                    "check_in": check_in_str,
                    "check_out": check_out_str,
                    "message": f"{available_count} kamar tersedia" if is_available else "Tidak ada kamar tersedia untuk tanggal tersebut"
                })
            else:
                print(f"Warning: Gagal mendapatkan data booking dari BookingService: {response.status_code}")
                return jsonify({
                    "type_code": type_code,
                    "available": True,
                    "warning": "Ketersediaan tidak dapat diverifikasi dengan akurat",
                    "message": "Tipe kamar aktif ditemukan, tetapi ketersediaan tidak dapat diverifikasi sepenuhnya"
                })
        except requests.exceptions.RequestException as e:
            print(f"Error saat menghubungi BookingService: {e}")
            return jsonify({
                "type_code": type_code,
                "available": True,
                "warning": "Ketersediaan tidak dapat diverifikasi dengan akurat",
                "message": "Tipe kamar aktif ditemukan, tetapi ketersediaan tidak dapat diverifikasi sepenuhnya"
            })
    except Exception as e:
        print(f"Error keika mengecek ketersediaan kamar: {e}")
        return jsonify({"error": "Kesalahan saat memeriksa ketersediaan", "details": str(e)}), 500

if __name__ == '__main__':
    # BOOKING_SERVICE_URL diperlukan jika ada cek booking saat delete
    BOOKING_SERVICE_URL = os.environ.get('BOOKING_SERVICE_URL', 'http://127.0.0.1:5002')
    with app.app_context():
        print(f"Mencoba terhubung ke database: {DB_URI}")
        try: 
            db.engine.connect(); print("Koneksi DB OK"); db.create_all()
            if not RoomType.query.first():
                 print("Tambah data awal RoomType...");
                 initial_rooms = [
                     RoomType(type_code='standard', name='Standard Room', price_per_night=500000, is_active=True),
                     RoomType(type_code='deluxe', name='Deluxe Room', price_per_night=800000, is_active=True),
                     RoomType(type_code='suite', name='Suite', price_per_night=1500000, is_active=True)
                 ]
                 db.session.add_all(initial_rooms); db.session.commit()
            print("Tabel siap.")
        except Exception as e: print(f"GAGAL KONEKSI ke Database: {e}"); import sys; sys.exit(1)
    print("Room service jalaan di port 5003 Euy")
    app.run(host='0.0.0.0', port=5003, debug=True)

