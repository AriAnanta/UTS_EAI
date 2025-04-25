from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import uuid
import random
import time
import os
import datetime
import requests
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import pickle

app = Flask(__name__)

@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}

GUEST_SERVICE_URL = os.environ.get('GUEST_SERVICE_URL', 'http://localhost:5001')
BOOKING_SERVICE_URL = os.environ.get('BOOKING_SERVICE_URL', 'http://localhost:5002')

# --- Konfigurasi Database MySQL ---
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_DB = os.environ.get('MYSQL_PAYMENT_DB', 'payment_db') 
MYSQL_PORT = os.environ.get('MYSQL_PORT', '3308')
DB_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Model Database ---
class PaymentTransaction(db.Model):
    __tablename__ = 'payment_transactions'
    id = db.Column(db.Integer, primary_key=True)
    payment_uid = db.Column(db.String(80), unique=True, nullable=False, default=lambda: f"pay_{uuid.uuid4()}")
    booking_uid = db.Column(db.String(80), nullable=False, index=True)
    requested_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), nullable=False, default='processing', index=True)
    message = db.Column(db.Text, nullable=True)
    failure_reason = db.Column(db.String(100), nullable=True)
    request_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    is_fraud = db.Column(db.Boolean, nullable=True, default=False)
    fraud_score = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            "payment_uid": self.payment_uid,
            "booking_uid": self.booking_uid,
            "requested_amount": self.requested_amount,
            "status": self.status,
            "message": self.message,
            "failure_reason": self.failure_reason,
            "request_time": self.request_time.isoformat() + "Z" if self.request_time else None,
            "processed_at": self.processed_at.isoformat() + "Z" if self.processed_at else None,
            "is_fraud": self.is_fraud,
            "fraud_score": self.fraud_score
        }

# Kelas untuk deteksi fraud
class FraudDetector:
    def __init__(self):
        self.model = None
        self.scaler = None
        print("Inisialisasi FraudDetector...")
        self.load_model()
    
    def load_model(self):
        try:
            self.model = joblib.load('fraud_model.joblib')
            self.scaler = joblib.load('scaler.joblib')
            print("Model fraud detection berhasil dimuat.")
        except Exception as e:
            print(f"Gagal memuat model: {e}")
            print("Model fraud detection belum ada. Membuat model baru...")
            self.train_model()
    
    def train_model(self):
        try:
            # Generate data dummy untuk pelatihan
            print("Memulai pelatihan model...")
            np.random.seed(42)
            n_samples = 1000
            
            # Fitur untuk model
            data = {
                'amount': np.random.uniform(500000, 5000000, n_samples),
                'time_to_process': np.random.uniform(30, 600, n_samples),  # waktu proses dalam detik
                'time_of_day': np.random.uniform(0, 24, n_samples),  # jam saat transaksi
                'day_of_week': np.random.randint(0, 7, n_samples),  # hari dalam seminggu (0=Senin, 6=Minggu)
                'booking_duration': np.random.randint(1, 14, n_samples),  # durasi menginap dalam hari
                'days_before_checkin': np.random.randint(1, 90, n_samples)  # berapa hari sebelum check-in
            }
            
            # Aturan sederhana untuk menentukan fraud dalam data dummy:
            # 1. Transaksi dengan jumlah sangat besar (> 4jt) dan proses cepat (< 60 detik)
            # 2. Transaksi tengah malam (jam 0-4) dengan durasi panjang (>7 hari)
            # 3. Transaksi hari Minggu dengan jumlah besar
            is_fraud = np.zeros(n_samples, dtype=bool)
            for i in range(n_samples):
                if data['amount'][i] > 4000000 and data['time_to_process'][i] < 60:
                    is_fraud[i] = np.random.random() < 0.8  # 80% kemungkinan fraud
                elif data['time_of_day'][i] < 4 and data['booking_duration'][i] > 7:
                    is_fraud[i] = np.random.random() < 0.7  # 70% kemungkinan fraud
                elif data['day_of_week'][i] == 6 and data['amount'][i] > 3500000:
                    is_fraud[i] = np.random.random() < 0.6  # 60% kemungkinan fraud
                else:
                    is_fraud[i] = np.random.random() < 0.05  # 5% baseline fraud
            
            # Buat DataFrame
            df = pd.DataFrame(data)
            X = df.values
            y = is_fraud
            
            print(f"Data pelatihan dibuat: {n_samples} sampel, {sum(is_fraud)} fraud cases")
            
            # Scaling fitur
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model Random Forest
            print("Melatih model Random Forest...")
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_scaled, y)
            
            try:
                joblib.dump(self.model, 'fraud_model.joblib')
                joblib.dump(self.scaler, 'scaler.joblib')
                print("Model fraud detection berhasil dilatih dan disimpan.")
            except Exception as save_err:
                print(f"Peringatan: Model berhasil dilatih tetapi gagal disimpan: {save_err}")
        except Exception as e:
            print(f"ERROR FATAL saat melatih model: {e}")
            import traceback
            traceback.print_exc()
            print("Membuat model default sebagai fallback...")
            self.model = RandomForestClassifier(n_estimators=10, random_state=42)
            self.scaler = StandardScaler()
            # Data minimal untuk fit scaler
            X_minimal = np.array([[1000000, 120, 12, 3, 2, 30], 
                                 [2000000, 60, 15, 5, 3, 14]])
            y_minimal = np.array([0, 1])
            self.scaler.fit(X_minimal)
            self.model.fit(X_minimal, y_minimal)
    
    def extract_features(self, transaction, booking_data=None):
        """Ekstrak fitur dari transaksi untuk prediksi fraud"""
        try:
            features = {}
            
            features['amount'] = float(transaction.requested_amount)
            
            # Waktu pemrosesan (jika sudah diproses)
            if transaction.processed_at:
                process_time = (transaction.processed_at - transaction.request_time).total_seconds()
            else:
                process_time = 300  
            features['time_to_process'] = float(process_time)
            
            # Waktu transaksi dalam hari
            features['time_of_day'] = float(transaction.request_time.hour + transaction.request_time.minute/60)
            
            # Hari dalam seminggu (0=Senin, 6=Minggu)
            features['day_of_week'] = float(transaction.request_time.weekday())
            
            # Fitur dari booking jika tersedia
            if booking_data:
                try:
                    if 'check_in_date' in booking_data and 'check_out_date' in booking_data:
                        try:
                            
                            check_in = datetime.datetime.fromisoformat(booking_data.get('check_in_date').replace('Z', ''))
                            check_out = datetime.datetime.fromisoformat(booking_data.get('check_out_date').replace('Z', ''))
                        except:
                 # Coba format tanggal alternatif
                            try:
                                check_in = datetime.datetime.strptime(booking_data.get('check_in_date'), '%Y-%m-%d')
                                check_out = datetime.datetime.strptime(booking_data.get('check_out_date'), '%Y-%m-%d')
                            except:
                                # Gunakan nilai default
                                print(f"Error parsing tanggal booking: {booking_data.get('check_in_date')}, {booking_data.get('check_out_date')}")
                                features['booking_duration'] = 2.0
                                features['days_before_checkin'] = 30.0
                                return np.array([[features[f] for f in ['amount', 'time_to_process', 'time_of_day', 'day_of_week', 'booking_duration', 'days_before_checkin']]])
                        
                        # Durasi menginap dalam hari
                        features['booking_duration'] = float((check_out - check_in).days)
                        
                        # Berapa hari sebelum check-in
                        days_before = (check_in - transaction.request_time).days
                        features['days_before_checkin'] = float(max(0, days_before)) 
                    else:
                        print("Data booking tidak memiliki tanggal check-in/check-out")
                        features['booking_duration'] = 2.0
                        features['days_before_checkin'] = 30.0
                except Exception as be:
                    print(f"Error saat ekstrak fitur dari booking data: {be}")
                    features['booking_duration'] = 2.0
                    features['days_before_checkin'] = 30.0
            else:
                features['booking_duration'] = 2.0
                features['days_before_checkin'] = 30.0
            
            feature_names = ['amount', 'time_to_process', 'time_of_day', 'day_of_week', 
                            'booking_duration', 'days_before_checkin']
            X = np.array([[float(features[f]) for f in feature_names]])
            return X
        except Exception as e:
            print(f"Error saat ekstrak fitur: {e}")
            return np.array([[float(transaction.requested_amount), 300.0, 12.0, 3.0, 2.0, 30.0]])
    
    def predict_fraud(self, transaction, booking_data=None):
        """Memprediksi apakah transaksi berpotensi fraud"""
        try:
            if not self.model or not self.scaler:
                print("Model atau scaler belum siap. Menggunakan nilai default")
                return False, 0.0
                
            X = self.extract_features(transaction, booking_data)
            X_scaled = self.scaler.transform(X)
            
            # Prediksi probabilitas fraud
            fraud_proba = self.model.predict_proba(X_scaled)[0, 1]
            
            # Prediksi binary (fraud atau tidak)
            is_fraud = fraud_proba > 0.7 
            
            return bool(is_fraud), float(fraud_proba)
        except Exception as e:
            print(f"Error saat memprediksi fraud: {e}")
    
            if transaction.is_fraud is not None and transaction.fraud_score is not None:
                return bool(transaction.is_fraud), float(transaction.fraud_score)
            # Jika tidak ada, nilai default
            return False, 0.0

# Inisialisasi fraud detector
fraud_detector = FraudDetector()

# Membuat data payment baru
@app.route('/payments', methods=['POST'])
def process_payment():
    """Memulai pemrosesan pembayaran, memverifikasi dengan layanan lain, dan menyimpan transaksi ke DB."""
    data = request.get_json()
    required = ['booking_uid', 'amount']
    if not data or not all(field in data for field in required):
        return jsonify({"error": f"Data tidak lengkap ({', '.join(required)})"}), 400

    booking_uid = data['booking_uid']
    try:
        amount_float = float(data['amount'])
        if amount_float <= 0: raise ValueError("Jumlah harus positif")
    except (ValueError, TypeError):
        return jsonify({"error": "Nilai 'amount' tidak valid atau tidak positif"}), 400

    try:
        booking_url = f"{BOOKING_SERVICE_URL}/bookings/{booking_uid}"
        print(f"Memverifikasi booking di: {booking_url}")
        booking_response = requests.get(booking_url, timeout=5) 
        booking_response.raise_for_status() 
        booking_data = booking_response.json()
        print(f"Data booking diterima: {booking_data}")

        # Verifikasi status booking (misal harus 'pending_payment')
        if booking_data.get('status') != 'pending_payment':
            return jsonify({"error": f"Booking {booking_uid} tidak dalam status 'pending_payment' (status saat ini: {booking_data.get('status')})"}), 400

        # Verifikasi jumlah pembayaran
        if abs(booking_data.get('total_price', 0) - amount_float) > 0.01: 
            return jsonify({"error": f"Jumlah pembayaran ({amount_float}) tidak sesuai dengan tagihan booking ({booking_data.get('total_price')})"}), 400

        guest_uid = booking_data.get('guest_uid')
        if not guest_uid:
            return jsonify({"error": "Guest UID tidak ditemukan dalam data booking"}), 400

    except requests.exceptions.RequestException as e:
        print(f"Error saat menghubungi Booking Service: {e}")
        return jsonify({"error": "Gagal menghubungi Booking Service", "details": str(e)}), 503 
    except Exception as e:
        print(f"Error saat memproses data booking: {e}")
        return jsonify({"error": "Gagal memproses data booking", "details": str(e)}), 500

    try:
        guest_url = f"{GUEST_SERVICE_URL}/guests/{guest_uid}"
        print(f"Memverifikasi guest di: {guest_url}")
        guest_response = requests.get(guest_url, timeout=5)
        guest_response.raise_for_status()
        guest_data = guest_response.json()
        print(f"Data guest diterima: {guest_data}")
        if guest_data.get('is_deleted'): 
             return jsonify({"error": f"Guest {guest_uid} tidak valid atau sudah dihapus"}), 400

    except requests.exceptions.RequestException as e:
        print(f"Error saat menghubungi Guest Service: {e}")
        return jsonify({"error": "Gagal menghubungi Guest Service", "details": str(e)}), 503
    except Exception as e:
        print(f"Error saat memproses data guest: {e}")
        return jsonify({"error": "Gagal memproses data guest", "details": str(e)}), 500

    print(f"Verifikasi untuk booking {booking_uid} dan guest {guest_uid} berhasil.")

    new_transaction = PaymentTransaction(
        booking_uid=booking_uid,
        requested_amount=amount_float,
        status='processing',
        message='Pembayaran sedang diproses...'
        # payment_uid dan request_time diisi default oleh model/DB
    )
    try:
        db.session.add(new_transaction)
        db.session.commit()
        # Ambil payment_uid yang baru dibuat
        payment_uid = new_transaction.payment_uid
        print(f"Menerima permintaan pembayaran {payment_uid} untuk booking {booking_uid}, sejumlah {amount_float}. Tersimpan ke DB.")
    except Exception as e:
        db.session.rollback()
        print(f"Database error saat membuat record payment awal: {e}")
        return jsonify({"error": "Gagal memulai transaksi pembayaran", "details": str(e)}), 500

    # 2Simulasi Proses Pembayaran Eksternal
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)
    processed_time = datetime.datetime.utcnow()
    is_success = random.random() < 0.85 # 85% kesempatan untuk suksesnya

    status = "success" if is_success else "failed"
    message = "Pembayaran berhasil diproses." if is_success else f"Pembayaran gagal: {random.choice(['INSUFFICIENT_FUNDS', 'CARD_DECLINED', 'TECHNICAL_ERROR', 'GATEWAY_TIMEOUT', 'SUSPECTED_FRAUD'])}"
    failure_reason = message.split(': ')[1] if status == 'failed' else None

    # 3Deteksi Fraud dengan Model ML
    try:
        transaction_to_update = PaymentTransaction.query.filter_by(payment_uid=payment_uid).first()
        # Prediksi fraud hanya jika pembayaran berhasil
        if status == "success":
            is_fraud, fraud_score = fraud_detector.predict_fraud(transaction_to_update, booking_data)
            transaction_to_update.is_fraud = is_fraud
            transaction_to_update.fraud_score = fraud_score
            
            # Jika terdeteksi fraud dengan confidence tinggi (>0.85), tolak otomatis 
            if is_fraud and fraud_score > 0.85:
                status = "failed"
                message = "Pembayaran ditolak: TERDETEKSI FRAUD"
                failure_reason = "FRAUD_DETECTION"
                transaction_to_update.is_fraud = True
                print(f"Transaksi {payment_uid} terdeteksi sebagai FRAUD dengan skor {fraud_score}. Ditolak otomatis.")
            elif is_fraud:
                # Fraud terdeteksi tapi dengan confidence medium, beri tanda tapi tetap proses
                print(f"Transaksi {payment_uid} mencurigakan (skor fraud: {fraud_score}), tapi tetap diproses.")
                message += " Transaksi mencurigakan. Tim keamanan akan memeriksa."
    except Exception as e:
        print(f"Error saat melakukan deteksi fraud: {e}")

    # 4. Update record transaksi di DB dengan hasil simulasi
    try:
        if not transaction_to_update:
            print(f"CRITICAL ERROR: Transaksi {payment_uid} tidak ditemukan untuk diupdate!")
            return jsonify({"error": "Konsistensi data error setelah simulasi"}), 500

        transaction_to_update.status = status
        transaction_to_update.message = message
        transaction_to_update.failure_reason = failure_reason
        transaction_to_update.processed_at = processed_time

        # Jika pembayaran sukses, update status booking di BookingService
        if status == "success":
            try:
                # Panggil endpoint update status di BookingService
                update_url = f"{BOOKING_SERVICE_URL}/bookings/{booking_uid}/confirm-payment"
                update_data = {
                    "payment_uid": payment_uid,
                    "amount": amount_float
                }
                update_response = requests.put(update_url, json=update_data, timeout=5)
                
                if not update_response.ok:
                    print(f"Gagal update status booking: {update_response.status_code}")
                    # Jika gagal update booking, tetap simpan transaksi tapi beri warning
                    transaction_to_update.message = "Pembayaran berhasil tapi gagal update status booking"
                    failure_reason = f"Booking update failed: {update_response.text}"
            except requests.exceptions.RequestException as e:
                print(f"Error saat update status booking: {str(e)}")
                transaction_to_update.message = "Pembayaran berhasil tapi gagal update status booking"
                failure_reason = f"Booking update error: {str(e)}"

        db.session.commit()
        print(f"Transaksi {payment_uid} selesai diproses. Status: {status}. Tersimpan ke DB.")
        return jsonify(transaction_to_update.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Database error saat mengupdate status payment: {e}")
        return jsonify({"error": "Gagal mengupdate status transaksi setelah proses", "details": str(e)}), 500


# Mengambil data payment berdasarkan payment_uid
@app.route('/payments/<payment_uid>', methods=['GET'])
def get_payment_status(payment_uid):
    """Mendapatkan status transaksi pembayaran berdasarkan payment_uid dari DB."""
    try:
        transaction = PaymentTransaction.query.filter_by(payment_uid=payment_uid).first()
        if transaction:
            return jsonify(transaction.to_dict()), 200
        else:
            return jsonify({"error": "Transaksi pembayaran tidak ditemukan"}), 404
    except Exception as e:
        print(f"Database error saat get_payment_status: {e}")
        return jsonify({"error": "Kesalahan database", "details": str(e)}), 500

# Baca semua data payment
@app.route('/payments', methods=['GET'])
def get_all_payments():
    """Mendapatkan daftar semua transaksi pembayaran dari DB."""
    booking_filter = request.args.get('booking_uid')
    status_filter = request.args.get('status')

    try:
        query = PaymentTransaction.query
        if booking_filter:
            query = query.filter(PaymentTransaction.booking_uid == booking_filter)
        if status_filter:
            query = query.filter(PaymentTransaction.status == status_filter)

        transactions = query.order_by(PaymentTransaction.request_time.desc()).all()
        return jsonify([t.to_dict() for t in transactions])
    except Exception as e:
        print(f"Database error saat get_all_payments: {e}")
        return jsonify({"error": "Kesalahan database", "details": str(e)}), 500

# Fraud Detection
@app.route('/payments/fraud-analysis', methods=['GET'])
def get_fraud_analysis():
    """Mendapatkan analisis fraud dari semua transaksi."""
    try:
        print("Mengakses endpoint /payments/fraud-analysis")
        
        # Ambil semua transaksi dengan status success yang terdeteksi fraud
        fraud_transactions = PaymentTransaction.query.filter(
            PaymentTransaction.is_fraud == True
        ).order_by(PaymentTransaction.fraud_score.desc()).all()
        
        print(f"Jumlah transaksi fraud terdeteksi: {len(fraud_transactions)}")
        
        # Ambil semua transaksi sukses
        all_success = PaymentTransaction.query.filter_by(status='success').count()
        fraud_count = len([t for t in fraud_transactions if t.status == 'success'])
        
        # Hitung statistik
        total_transactions = PaymentTransaction.query.count()
        fraud_percentage = 0
        if all_success > 0:
            fraud_percentage = (fraud_count / all_success) * 100
            
        print(f"Total: {total_transactions}, Success: {all_success}, Fraud: {fraud_count}, Percentage: {fraud_percentage}%")
        
        result = {
            "total_transactions": total_transactions,
            "total_success_transactions": all_success,
            "total_fraud_detected": fraud_count,
            "fraud_percentage": fraud_percentage,
            "fraud_transactions": [t.to_dict() for t in fraud_transactions[:10]]  # Limit ke 10 transaksi
        }
        
        print("Sukses mengambil analisis fraud")
        return jsonify(result), 200
    except Exception as e:
        print(f"ERROR saat mengambil analisis fraud: {e}")
        import traceback
        traceback.print_exc()
        
        # Dalam keadaan error, kirim data default
        return jsonify({
            "error": f"Gagal mendapatkan analisis fraud: {str(e)}",
            "total_transactions": 0,
            "total_success_transactions": 0,
            "total_fraud_detected": 0,
            "fraud_percentage": 0,
            "fraud_transactions": []
        }), 500

@app.route('/payments/<payment_uid>/analyze-fraud', methods=['GET'])
def analyze_payment_fraud(payment_uid):
    """Menganalisis satu transaksi pembayaran untuk deteksi fraud."""
    try:
        print(f"Mengakses endpoint /payments/{payment_uid}/analyze-fraud")
        # Ambil data transaksi
        transaction = PaymentTransaction.query.filter_by(payment_uid=payment_uid).first()
        if not transaction:
            return jsonify({"error": "Transaksi pembayaran tidak ditemukan"}), 404
        
        print(f"Transaksi ditemukan: {payment_uid}, status: {transaction.status}")
        
        # Ambil data booking
        booking_data = None
        try:
            booking_response = requests.get(f"{BOOKING_SERVICE_URL}/bookings/{transaction.booking_uid}", timeout=5)
            if booking_response.ok:
                booking_data = booking_response.json()
                print(f"Data booking diperoleh: {transaction.booking_uid}")
            else:
                print(f"Gagal mendapatkan data booking: {booking_response.status_code}")
        except Exception as be:
            print(f"Error saat mengambil data booking: {str(be)}")
        
        # Lakukan prediksi fraud (meskipun sudah ada nilai sebelumnya)
        is_fraud, fraud_score = False, 0.0
        try:
            is_fraud, fraud_score = fraud_detector.predict_fraud(transaction, booking_data)
            print(f"Hasil prediksi fraud: {is_fraud}, skor: {fraud_score}")
        except Exception as fe:
            print(f"Error saat memprediksi fraud: {str(fe)}")
            # Gunakan nilai dari database jika prediksi gagal
            is_fraud = transaction.is_fraud or False
            fraud_score = transaction.fraud_score or 0.0
        
        # Ambil fitur yang digunakan untuk prediksi
        features = []
        feature_names = ['Jumlah (Rp)', 'Waktu Proses (detik)', 'Waktu Hari (jam)', 'Hari Minggu (0-6)', 
                         'Durasi Booking (hari)', 'Hari Sebelum Check-in']
        
        try:
            features = fraud_detector.extract_features(transaction, booking_data)[0].tolist()
            print(f"Berhasil mengekstrak fitur: {len(features)} fitur")
        except Exception as ee:
            print(f"Error saat mengekstrak fitur: {str(ee)}")
            # Gunakan nilai default jika ekstraksi fitur gagal
            features = [transaction.requested_amount, 300, 12, 1, 2, 30]
        
        # Hitung skor fitur terhadap fraud
        feature_importance = []
        try:
            if fraud_detector.model:
                importance = fraud_detector.model.feature_importances_
                for i, (name, value, imp) in enumerate(zip(feature_names, features, importance)):
                    feature_importance.append({
                        "name": name,
                        "value": value,
                        "importance": float(imp),
                        "contribution": float(value * imp)
                    })
                print(f"Berhasil menghitung feature importance")
            else:
                # Jika model belum siap, buat nilai default
                for i, (name, value) in enumerate(zip(feature_names, features)):
                    feature_importance.append({
                        "name": name,
                        "value": value,
                        "importance": 0.1,
                        "contribution": 0.1
                    })
        except Exception as me:
            print(f"Error saat menghitung feature importance: {str(me)}")
            # Buat feature importance default jika terjadi error
            for i, (name, value) in enumerate(zip(feature_names, features)):
                feature_importance.append({
                    "name": name,
                    "value": value,
                    "importance": 0.1,
                    "contribution": 0.1
                })
        
        # Kirim hasil analisis
        result = {
            "payment_uid": payment_uid,
            "transaction": transaction.to_dict(),
            "fraud_analysis": {
                "is_fraud": bool(is_fraud),
                "fraud_score": float(fraud_score),
                "fraud_threshold": 0.7,
                "high_risk_threshold": 0.85,
                "features": [{"name": name, "value": float(value)} for name, value in zip(feature_names, features)],
                "feature_importance": feature_importance,
                "risk_level": "Tinggi" if fraud_score > 0.85 else ("Sedang" if fraud_score > 0.7 else "Rendah")
            }
        }
        
        print(f"Berhasil menganalisis fraud untuk transaksi {payment_uid}")
        return jsonify(result), 200
    except Exception as e:
        print(f"ERROR saat menganalisis fraud: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "error": f"Gagal menganalisis fraud: {str(e)}",
            "payment_uid": payment_uid,
            "transaction": {"payment_uid": payment_uid, "status": "unknown"},
            "fraud_analysis": {
                "is_fraud": False,
                "fraud_score": 0,
                "features": [],
                "feature_importance": [],
                "risk_level": "Tidak dapat ditentukan"
            }
        }), 500

if __name__ == '__main__':
    with app.app_context():
        print(f"Mencoba terhubung ke database: {DB_URI}")
        try:
            db.engine.connect()
            print("Koneksi database berhasil. Membuat tabel jika belum ada...")
            db.create_all() # Membuat tabel payment_transactions jika belum ada
            print("Tabel siap.")
        except Exception as e:
            print(f"GAGAL terhubung ke database atau membuat tabel: {e}")
            print("Pastikan server MySQL berjalan, database payment_db sudah dibuat, dan kredensial benar.")
            import sys
            sys.exit(1)

    print("Starting PaymentService (with Database) on port 5004...")
    app.run(host='0.0.0.0', port=5004, debug=True)

