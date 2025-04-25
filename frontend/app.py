from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import requests
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'hotelazurehorizonhotelsecretkey123'

# --- Konfigurasi URL Service ---
GUEST_SERVICE_URL = os.environ.get('GUEST_SERVICE_URL', 'http://localhost:5001')
BOOKING_SERVICE_URL = os.environ.get('BOOKING_SERVICE_URL', 'http://localhost:5002')
ROOM_SERVICE_URL = os.environ.get('ROOM_SERVICE_URL', 'http://localhost:5003')
PAYMENT_SERVICE_URL = os.environ.get('PAYMENT_SERVICE_URL', 'http://localhost:5004')

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# --- Routes ---
@app.route('/')
def index():
    """Halaman utama hotel management system"""
    return render_template('index.html')

# --- Routes untuk Manajemen Tamu ---
@app.route('/guests')
def list_guests():
    """Menampilkan daftar tamu"""
    try:
        response = requests.get(f"{GUEST_SERVICE_URL}/guests")
        if response.ok:
            guests = response.json()
            return render_template('guests/list.html', guests=guests)
        else:
            flash(f"Gagal mengambil data tamu: {response.status_code}", "danger")
            return render_template('guests/list.html', guests=[])
    except requests.RequestException as e:
        flash(f"Error terhubung ke Guest Service: {str(e)}", "danger")
        return render_template('guests/list.html', guests=[])

@app.route('/guests/add', methods=['GET', 'POST'])
def add_guest():
    """Form untuk menambahkan tamu baru"""
    if request.method == 'POST':
        guest_data = {
            'guest_uid': request.form.get('guest_uid'),
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone')
        }
        
        try:
            response = requests.post(f"{GUEST_SERVICE_URL}/guests", json=guest_data)
            if response.ok:
                flash("Tamu berhasil ditambahkan", "success")
                return redirect(url_for('list_guests'))
            else:
                error_data = response.json()
                flash(f"Gagal menambahkan tamu: {error_data.get('error', 'Unknown error')}", "danger")
        except requests.RequestException as e:
            flash(f"Error terhubung ke Guest Service: {str(e)}", "danger")
            
    return render_template('guests/add.html')

@app.route('/guests/<guest_uid>')
def view_guest(guest_uid):
    """Melihat detail tamu"""
    try:
        # Ambil detail tamu
        guest_response = requests.get(f"{GUEST_SERVICE_URL}/guests/{guest_uid}")
        if not guest_response.ok:
            flash(f"Gagal mengambil data tamu: {guest_response.status_code}", "danger")
            return redirect(url_for('list_guests'))
        
        guest = guest_response.json()
        
        # Ambil booking tamu
        booking_response = requests.get(f"{GUEST_SERVICE_URL}/guests/{guest_uid}/bookings")
        if booking_response.ok:
            bookings = booking_response.json()
        else:
            bookings = []
            flash("Gagal mengambil riwayat booking", "warning")
            
        return render_template('guests/detail.html', guest=guest, bookings=bookings)
    except requests.RequestException as e:
        flash(f"Error terhubung ke service: {str(e)}", "danger")
        return redirect(url_for('list_guests'))

@app.route('/guests/<guest_uid>/edit', methods=['GET', 'POST'])
def edit_guest(guest_uid):
    """Form untuk mengedit data tamu"""
    if request.method == 'GET':
        try:
            response = requests.get(f"{GUEST_SERVICE_URL}/guests/{guest_uid}")
            if response.ok:
                guest = response.json()
                return render_template('guests/edit.html', guest=guest)
            else:
                flash(f"Gagal mengambil data tamu: {response.status_code}", "danger")
                return redirect(url_for('list_guests'))
        except requests.RequestException as e:
            flash(f"Error terhubung ke Guest Service: {str(e)}", "danger")
            return redirect(url_for('list_guests'))
    
    elif request.method == 'POST':
        guest_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone')
        }
        
        try:
            response = requests.put(f"{GUEST_SERVICE_URL}/guests/{guest_uid}", json=guest_data)
            if response.ok:
                flash("Data tamu berhasil diperbarui", "success")
                return redirect(url_for('view_guest', guest_uid=guest_uid))
            else:
                error_data = response.json()
                flash(f"Gagal memperbarui data tamu: {error_data.get('error', 'Unknown error')}", "danger")
                return render_template('guests/edit.html', guest=guest_data)
        except requests.RequestException as e:
            flash(f"Error terhubung ke Guest Service: {str(e)}", "danger")
            return render_template('guests/edit.html', guest=guest_data)

@app.route('/guests/<guest_uid>/delete', methods=['POST'])
def delete_guest(guest_uid):
    """Menghapus data tamu"""
    try:
        response = requests.delete(f"{GUEST_SERVICE_URL}/guests/{guest_uid}")
        if response.ok:
            flash("Data tamu berhasil dihapus", "success")
        else:
            error_data = response.json()
            flash(f"Gagal menghapus tamu: {error_data.get('error', 'Unknown error')}", "danger")
    except requests.RequestException as e:
        flash(f"Error terhubung ke Guest Service: {str(e)}", "danger")
        
    return redirect(url_for('list_guests'))

# --- Routes untuk Manajemen Kamar ---
@app.route('/rooms')
def list_rooms():
    """Menampilkan daftar tipe kamar"""
    try:
        response = requests.get(f"{ROOM_SERVICE_URL}/rooms")
        if response.ok:
            rooms = response.json()
            return render_template('rooms/list.html', rooms=rooms)
        else:
            flash(f"Gagal mengambil data kamar: {response.status_code}", "danger")
            return render_template('rooms/list.html', rooms=[])
    except requests.RequestException as e:
        flash(f"Error terhubung ke Room Service: {str(e)}", "danger")
        return render_template('rooms/list.html', rooms=[])

@app.route('/rooms/add', methods=['GET', 'POST'])
def add_room_type():
    """Form untuk menambahkan tipe kamar baru"""
    if request.method == 'POST':
        room_data = {
            'type_code': request.form.get('type_code'),
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price_per_night': float(request.form.get('price_per_night', 0))
        }
        
        try:
            response = requests.post(f"{ROOM_SERVICE_URL}/rooms", json=room_data)
            if response.ok:
                flash("Tipe kamar berhasil ditambahkan", "success")
                return redirect(url_for('list_rooms'))
            else:
                error_data = response.json()
                flash(f"Gagal menambahkan tipe kamar: {error_data.get('error', 'Unknown error')}", "danger")
        except requests.RequestException as e:
            flash(f"Error terhubung ke Room Service: {str(e)}", "danger")
            
    return render_template('rooms/add.html')

@app.route('/rooms/<type_code>')
def view_room(type_code):
    """Melihat detail tipe kamar"""
    try:
        response = requests.get(f"{ROOM_SERVICE_URL}/rooms/{type_code}")
        if response.ok:
            room = response.json()
            return render_template('rooms/detail.html', room=room)
        else:
            flash(f"Gagal mengambil detail kamar: {response.status_code}", "danger")
            return redirect(url_for('list_rooms'))
    except requests.RequestException as e:
        flash(f"Error terhubung ke Room Service: {str(e)}", "danger")
        return redirect(url_for('list_rooms'))

@app.route('/rooms/<type_code>/edit', methods=['GET', 'POST'])
def edit_room(type_code):
    """Form untuk mengedit tipe kamar"""
    if request.method == 'GET':
        try:
            response = requests.get(f"{ROOM_SERVICE_URL}/rooms/{type_code}")
            if response.ok:
                room = response.json()
                return render_template('rooms/edit.html', room=room)
            else:
                flash(f"Gagal mengambil detail kamar: {response.status_code}", "danger")
                return redirect(url_for('list_rooms'))
        except requests.RequestException as e:
            flash(f"Error terhubung ke Room Service: {str(e)}", "danger")
            return redirect(url_for('list_rooms'))
    
    elif request.method == 'POST':
        room_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price_per_night': float(request.form.get('price_per_night', 0))
        }
        
        try:
            response = requests.put(f"{ROOM_SERVICE_URL}/rooms/{type_code}", json=room_data)
            if response.ok:
                flash("Tipe kamar berhasil diperbarui", "success")
                return redirect(url_for('view_room', type_code=type_code))
            else:
                error_data = response.json()
                flash(f"Gagal memperbarui tipe kamar: {error_data.get('error', 'Unknown error')}", "danger")
                return render_template('rooms/edit.html', room={**room_data, 'type_code': type_code})
        except requests.RequestException as e:
            flash(f"Error terhubung ke Room Service: {str(e)}", "danger")
            return render_template('rooms/edit.html', room={**room_data, 'type_code': type_code})

@app.route('/rooms/<type_code>/delete', methods=['POST'])
def delete_room(type_code):
    """Menghapus tipe kamar"""
    try:
        response = requests.delete(f"{ROOM_SERVICE_URL}/rooms/{type_code}")
        if response.ok:
            flash("Tipe kamar berhasil dihapus", "success")
        else:
            error_data = response.json()
            flash(f"Gagal menghapus tipe kamar: {error_data.get('error', 'Unknown error')}", "danger")
    except requests.RequestException as e:
        flash(f"Error terhubung ke Room Service: {str(e)}", "danger")
        
    return redirect(url_for('list_rooms'))

@app.route('/rooms/check-availability', methods=['GET', 'POST'])
def check_room_availability():
    """Form untuk mengecek ketersediaan kamar"""
    if request.method == 'POST':
        type_code = request.form.get('type_code')
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')
        
        try:
            response = requests.get(
                f"{ROOM_SERVICE_URL}/rooms/{type_code}/availability",
                params={'check_in': check_in, 'check_out': check_out}
            )
            
            if response.ok:
                availability = response.json()
                return render_template('rooms/availability_result.html', availability=availability)
            else:
                error_data = response.json()
                flash(f"Gagal mengecek ketersediaan: {error_data.get('error', 'Unknown error')}", "danger")
        except requests.RequestException as e:
            flash(f"Error terhubung ke Room Service: {str(e)}", "danger")
    
    # Ambil semua tipe kamar untuk dropdown
    try:
        rooms_response = requests.get(f"{ROOM_SERVICE_URL}/rooms")
        if rooms_response.ok:
            rooms = rooms_response.json()
        else:
            rooms = []
            flash("Gagal memuat daftar tipe kamar", "warning")
    except:
        rooms = []
        
    return render_template('rooms/check_availability.html', rooms=rooms)

# --- Routes untuk Booking ---
@app.route('/bookings')
def list_bookings():
    """Menampilkan daftar booking"""
    try:
        response = requests.get(f"{BOOKING_SERVICE_URL}/bookings")
        if response.ok:
            bookings = response.json()
            return render_template('bookings/list.html', bookings=bookings)
        else:
            flash(f"Gagal mengambil data booking: {response.status_code}", "danger")
            return render_template('bookings/list.html', bookings=[])
    except requests.RequestException as e:
        flash(f"Error terhubung ke Booking Service: {str(e)}", "danger")
        return render_template('bookings/list.html', bookings=[])

@app.route('/bookings/add', methods=['GET', 'POST'])
def add_booking():
    """Form untuk menambahkan booking baru"""
    if request.method == 'GET':
        # Ambil daftar tamu untuk dropdown
        try:
            guests_response = requests.get(f"{GUEST_SERVICE_URL}/guests")
            if guests_response.ok:
                guests = guests_response.json()
            else:
                guests = []
                flash("Gagal memuat daftar tamu", "warning")
        except:
            guests = []
            
        # Ambil daftar tipe kamar untuk dropdown
        try:
            rooms_response = requests.get(f"{ROOM_SERVICE_URL}/rooms")
            if rooms_response.ok:
                rooms = rooms_response.json()
            else:
                rooms = []
                flash("Gagal memuat daftar tipe kamar", "warning")
        except:
            rooms = []
            
        return render_template('bookings/add.html', guests=guests, rooms=rooms)
    
    elif request.method == 'POST':
        booking_data = {
            'guest_uid': request.form.get('guest_uid'),
            'room_type_code': request.form.get('room_type_code'),
            'check_in': request.form.get('check_in'),
            'check_out': request.form.get('check_out')
        }
        
        try:
            response = requests.post(f"{BOOKING_SERVICE_URL}/bookings", json=booking_data)
            if response.ok:
                flash("Booking berhasil dibuat", "success")
                return redirect(url_for('list_bookings'))
            else:
                error_data = response.json()
                flash(f"Gagal membuat booking: {error_data.get('error', 'Unknown error')}", "danger")
                return redirect(url_for('add_booking'))
        except requests.RequestException as e:
            flash(f"Error terhubung ke Booking Service: {str(e)}", "danger")
            return redirect(url_for('add_booking'))

@app.route('/bookings/<booking_uid>')
def view_booking(booking_uid):
    """Melihat detail booking"""
    try:
        response = requests.get(f"{BOOKING_SERVICE_URL}/bookings/{booking_uid}")
        if response.ok:
            booking = response.json()
            
            # Ambil informasi tamu
            try:
                guest_response = requests.get(f"{GUEST_SERVICE_URL}/guests/{booking['guest_uid']}")
                if guest_response.ok:
                    guest = guest_response.json()
                else:
                    guest = {'name': 'Informasi tamu tidak tersedia'}
            except:
                guest = {'name': 'Informasi tamu tidak tersedia'}
                
            # Ambil informasi kamar
            try:
                room_response = requests.get(f"{ROOM_SERVICE_URL}/rooms/{booking['room_type_code']}")
                if room_response.ok:
                    room = room_response.json()
                else:
                    room = {'name': 'Informasi kamar tidak tersedia'}
            except:
                room = {'name': 'Informasi kamar tidak tersedia'}
                
            # Ambil informasi pembayaran 
            payment = None
            if booking.get('payment_id'):
                try:
                    payment_response = requests.get(f"{PAYMENT_SERVICE_URL}/payments/{booking['payment_id']}")
                    if payment_response.ok:
                        payment = payment_response.json()
                except:
                    pass
            
            return render_template(
                'bookings/detail.html',
                booking=booking,
                guest=guest,
                room=room,
                payment=payment
            )
        else:
            flash(f"Gagal mengambil detail booking: {response.status_code}", "danger")
            return redirect(url_for('list_bookings'))
    except requests.RequestException as e:
        flash(f"Error terhubung ke service: {str(e)}", "danger")
        return redirect(url_for('list_bookings'))

@app.route('/bookings/<booking_uid>/cancel', methods=['POST'])
def cancel_booking(booking_uid):
    """Membatalkan booking"""
    reason = request.form.get('reason', 'Dibatalkan oleh pengguna')
    
    try:
        response = requests.put(
            f"{BOOKING_SERVICE_URL}/bookings/{booking_uid}/cancel",
            json={'reason': reason}
        )
        
        if response.ok:
            flash("Booking berhasil dibatalkan", "success")
        else:
            error_data = response.json()
            flash(f"Gagal membatalkan booking: {error_data.get('error', 'Unknown error')}", "danger")
    except requests.RequestException as e:
        flash(f"Error terhubung ke Booking Service: {str(e)}", "danger")
        
    return redirect(url_for('view_booking', booking_uid=booking_uid))

# --- Routes untuk Payment ---
@app.route('/payments')
def list_payments():
    """Menampilkan daftar pembayaran"""
    try:
        response = requests.get(f"{PAYMENT_SERVICE_URL}/payments")
        if response.ok:
            payments = response.json()
            return render_template('payments/list.html', payments=payments)
        else:
            flash(f"Gagal mengambil data pembayaran: {response.status_code}", "danger")
            return render_template('payments/list.html', payments=[])
    except requests.RequestException as e:
        flash(f"Error terhubung ke Payment Service: {str(e)}", "danger")
        return render_template('payments/list.html', payments=[])

@app.route('/payments/<payment_uid>')
def view_payment(payment_uid):
    """Melihat detail pembayaran"""
    try:
        # Ambil detail pembayaran
        payment_response = requests.get(f"{PAYMENT_SERVICE_URL}/payments/{payment_uid}")
        if not payment_response.ok:
            flash(f"Gagal mengambil data pembayaran: {payment_response.status_code}", "danger")
            return redirect(url_for('list_payments'))
        
        payment = payment_response.json()
        
        # Ambil data booking
        booking_response = requests.get(f"{BOOKING_SERVICE_URL}/bookings/{payment['booking_uid']}")
        if booking_response.ok:
            booking = booking_response.json()
            try:
                # Ambil data tamu
                guest_response = requests.get(f"{GUEST_SERVICE_URL}/guests/{booking['guest_uid']}")
                if guest_response.ok:
                    guest = guest_response.json()
                    booking['guest_name'] = guest['name']
                else:
                    booking['guest_name'] = "Data tamu tidak tersedia"
                
                # Ambil data kamar
                room_response = requests.get(f"{ROOM_SERVICE_URL}/rooms/{booking['room_type_code']}")
                if room_response.ok:
                    room = room_response.json()
                    booking['room_name'] = room['name']
                else:
                    booking['room_name'] = "Data kamar tidak tersedia"
            except:
                booking['guest_name'] = "Data tamu tidak tersedia"
                booking['room_name'] = "Data kamar tidak tersedia"
        else:
            booking = None
            
        return render_template('payments/detail.html', payment=payment, booking=booking)
    except requests.RequestException as e:
        flash(f"Error terhubung ke service: {str(e)}", "danger")
        return redirect(url_for('list_payments'))

@app.route('/bookings/<booking_uid>/process-payment', methods=['POST'])
def process_payment(booking_uid):
    """Memproses pembayaran untuk booking"""
    try:
        booking_response = requests.get(f"{BOOKING_SERVICE_URL}/bookings/{booking_uid}")
        if not booking_response.ok:
            flash("Booking tidak ditemukan", "danger")
            return redirect(url_for('list_bookings'))
        
        booking = booking_response.json()

        if booking['status'] != 'pending_payment':
            flash("Booking ini tidak dalam status menunggu pembayaran", "warning")
            return redirect(url_for('view_booking', booking_uid=booking_uid))

        payment_data = {
            'booking_uid': booking_uid,
            'amount': booking['total_price']
        }
        
        response = requests.post(f"{PAYMENT_SERVICE_URL}/payments", json=payment_data)
        
        if response.ok:
            payment = response.json()
            
            if payment['status'] == 'success':
                flash("Pembayaran berhasil diproses", "success")
            elif payment['status'] == 'failed':
                flash(f"Pembayaran gagal: {payment.get('failure_reason', 'Unknown error')}", "danger")
            else:
                flash("Pembayaran sedang diproses", "info")
                
            return redirect(url_for('view_payment', payment_uid=payment['payment_uid']))
        else:
            error_msg = "Gagal memproses pembayaran"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_msg = error_data['error']
            except:
                pass
            
            flash(error_msg, "danger")
            return redirect(url_for('view_booking', booking_uid=booking_uid))
            
    except requests.RequestException as e:
        flash(f"Error terhubung ke Payment Service: {str(e)}", "danger")
        return redirect(url_for('view_booking', booking_uid=booking_uid))

# --- Routes untuk Fraud Detection ---
@app.route('/payments/fraud-analysis')
def view_fraud_analysis():
    """Menampilkan analisis fraud dari semua transaksi pembayaran"""
    try:
        # Ambil analisis fraud dari payment service
        print(f"Meminta data analisis fraud dari {PAYMENT_SERVICE_URL}/payments/fraud-analysis")
        response = requests.get(f"{PAYMENT_SERVICE_URL}/payments/fraud-analysis", timeout=10)
        
        if response.ok:
            print("Berhasil mendapatkan data analisis fraud")
            analysis = response.json()
            return render_template('payments/fraud_analysis.html', analysis=analysis)
        else:
            error_msg = f"Gagal mengambil data analisis fraud: {response.status_code}"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_msg = error_data['error']
                    print(f"Error dari server: {error_msg}")
            except:
                print(f"Tidak dapat parse response JSON: {response.text}")
                
            # Jika terjadi error, tampilkan template dengan data kosong
            flash(error_msg, "danger")
            dummy_analysis = {
                "total_transactions": 0,
                "total_success_transactions": 0,
                "total_fraud_detected": 0,
                "fraud_percentage": 0,
                "fraud_transactions": []
            }
            return render_template('payments/fraud_analysis.html', analysis=dummy_analysis)
    except requests.RequestException as e:
        print(f"Error koneksi ke Payment Service: {str(e)}")
        flash(f"Error terhubung ke Payment Service: {str(e)}", "danger")
        # Data dummy untuk ditampilkan saat terjadi error
        dummy_analysis = {
            "total_transactions": 0,
            "total_success_transactions": 0,
            "total_fraud_detected": 0,
            "fraud_percentage": 0,
            "fraud_transactions": []
        }
        return render_template('payments/fraud_analysis.html', analysis=dummy_analysis)

@app.route('/payments/<payment_uid>/fraud-analysis')
def view_fraud_detail(payment_uid):
    """Menampilkan detail analisis fraud dari satu transaksi pembayaran"""
    try:
        print(f"Meminta detail fraud untuk {payment_uid} dari {PAYMENT_SERVICE_URL}/payments/{payment_uid}/analyze-fraud")
        response = requests.get(f"{PAYMENT_SERVICE_URL}/payments/{payment_uid}/analyze-fraud", timeout=10)
        
        if response.ok:
            print(f"Berhasil mendapatkan analisis fraud untuk {payment_uid}")
            analysis = response.json()
            return render_template('payments/fraud_detail.html', analysis=analysis)
        else:
            error_msg = f"Gagal mengambil data analisis fraud: {response.status_code}"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_msg = error_data['error']
                    print(f"Error dari server: {error_msg}")
            except:
                print(f"Tidak dapat parse response JSON: {response.text}")
                
            flash(error_msg, "danger")
            return redirect(url_for('view_payment', payment_uid=payment_uid))
    except requests.RequestException as e:
        print(f"Error koneksi ke Payment Service: {str(e)}")
        flash(f"Error terhubung ke Payment Service: {str(e)}", "danger")
        return redirect(url_for('view_payment', payment_uid=payment_uid))

@app.route('/payments/<payment_uid>/flag-fraud', methods=['POST'])
def flag_payment_fraud(payment_uid):
    """Menandai transaksi pembayaran sebagai fraud"""
    try:
        flash(f"Fitur untuk menandai transaksi sebagai fraud belum diimplementasikan", "warning")
        return redirect(url_for('view_fraud_detail', payment_uid=payment_uid))
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('view_fraud_detail', payment_uid=payment_uid))

# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    """Halaman dashboard dengan ringkasan data"""
    data = {
        'guests_count': 0,
        'active_bookings': 0,
        'available_rooms': 0,
        'recent_bookings': [],
        'payment_stats': {
            'success': 0,
            'failed': 0,
            'processing': 0
        }
    }
    
    try:
        guests_response = requests.get(f"{GUEST_SERVICE_URL}/guests")
        if guests_response.ok:
            data['guests_count'] = len(guests_response.json())
    except:
        pass
        
    # booking aktif
    try:
        bookings_response = requests.get(f"{BOOKING_SERVICE_URL}/bookings?status=confirmed")
        if bookings_response.ok:
            bookings = bookings_response.json()
            # Filter yang check-out-nya di masa depan
            today = datetime.now().strftime('%Y-%m-%d')
            data['active_bookings'] = sum(1 for b in bookings if b.get('check_out_date', '') > today)
            # Ambil 5 booking terbaru
            data['recent_bookings'] = sorted(
                bookings,
                key=lambda b: b.get('booking_time', ''),
                reverse=True
            )[:5]
    except:
        pass
        
    # ambil jumlah tipe kamar yang tersedia
    try:
        rooms_response = requests.get(f"{ROOM_SERVICE_URL}/rooms")
        if rooms_response.ok:
            data['available_rooms'] = len(rooms_response.json())
    except:
        pass
        
    #  ambil statistik pembayaran
    try:
        payments_response = requests.get(f"{PAYMENT_SERVICE_URL}/payments")
        if payments_response.ok:
            payments = payments_response.json()
            for payment in payments:
                status = payment.get('status', '')
                if status == 'success':
                    data['payment_stats']['success'] += 1
                elif status == 'failed':
                    data['payment_stats']['failed'] += 1
                elif status == 'processing':
                    data['payment_stats']['processing'] += 1
    except:
        pass
        
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)