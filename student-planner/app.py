from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
import random

app = Flask(__name__)
# เพิ่ม Secret Key ตรงนี้ (ใส่คำว่าอะไรก็ได้)
app.config['SECRET_KEY'] = 'secretkey1234'

# ตั้งค่า Database SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planner.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# สร้างตารางเก็บข้อมูลงาน (Task)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    due_date = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Pending') # สถานะ: Pending หรือ Done

# สร้างตารางเก็บข้อมูลตารางเรียน (Subject)
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    day = db.Column(db.String(20))
    time = db.Column(db.String(50))
    room = db.Column(db.String(50))

# --- สร้างตารางเก็บข้อมูลผู้ใช้งาน (User) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

# Route หน้าแรก (บังคับ Login) 
@app.route('/')
def home():
    # ตรวจสอบว่ามีข้อมูลผู้ใช้ใน Session (ล็อกอินค้างไว้) หรือไม่
    if 'username' in session:
        return redirect(url_for('dashboard')) # ถ้าล็อกอินแล้ว ให้พาไปหน้างานของฉันเลย
    else:
        return redirect(url_for('login')) # ถ้ายังไม่ล็อกอิน ให้เด้งไปหน้าเข้าสู่ระบบ

# --- เพิ่มโค้ดส่วนนี้ต่อจากหน้า home() ---

@app.route('/dashboard')
def dashboard():
    # ดึงข้อมูลงานทั้งหมดจากฐานข้อมูลมาแสดง
    tasks = Task.query.all()
    return render_template('dashboard.html', tasks=tasks)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        # รับข้อมูลจากฟอร์ม HTML
        task_title = request.form['title']
        task_desc = request.form['description']
        task_due = request.form['due_date']
        
        # บันทึกลงฐานข้อมูล
        new_task = Task(title=task_title, description=task_desc, due_date=task_due)
        db.session.add(new_task)
        db.session.commit()
        
        return redirect(url_for('dashboard')) # บันทึกเสร็จเด้งไปหน้า Dashboard
    
    return render_template('add_task.html')

# --- ส่วนของ แก้ไข ลบ และเปลี่ยนสถานะงาน ---

@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    # ค้นหางานจาก ID ในฐานข้อมูล
    task = Task.query.get_or_404(id)
    
    if request.method == 'POST':
        # รับข้อมูลที่แก้ไขจากฟอร์ม
        task.title = request.form['title']
        task.description = request.form['description']
        task.due_date = request.form['due_date']
        task.status = request.form['status']
        
        db.session.commit() # บันทึกการแก้ไขลงฐานข้อมูล
        return redirect(url_for('dashboard'))
        
    return render_template('edit_task.html', task=task) # ส่งข้อมูลเดิมไปแสดงในฟอร์ม

@app.route('/delete_task/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/complete_task/<int:id>')
def complete_task(id):
    task = Task.query.get_or_404(id)
    task.status = 'Done'
    db.session.commit()
    return redirect(url_for('dashboard'))

# --- หน้าประวัติงานที่ทำเสร็จแล้ว ---
@app.route('/history')
def history():
    # ดึงเฉพาะงานที่มีสถานะ 'Done'
    tasks = Task.query.filter_by(status='Done').all()
    return render_template('history.html', tasks=tasks)

# --- ส่วนของตารางเรียน ---
@app.route('/schedule')
def schedule():
    subjects = Subject.query.all()
    
    # ลิสต์รายชื่อวัน
    days_info = [
        {"th": "วันจันทร์", "en": "Monday"},
        {"th": "วันอังคาร", "en": "Tuesday"},
        {"th": "วันพุธ", "en": "Wednesday"},
        {"th": "วันพฤหัสบดี", "en": "Thursday"},
        {"th": "วันศุกร์", "en": "Friday"}
    ]
    
    schedule_data = []
    subject_colors = {}
    processed_subjects = []
    
    # 1. คำนวณคอลัมน์เวลาและสุ่มสีให้วิชา
    for sub in subjects:
        try:
            start_t, end_t = sub.time.split('-')
            start_h, start_m = map(int, start_t.split(':'))
            end_h, end_m = map(int, end_t.split(':'))
            
            start_col = 2 + ((start_h - 8) * 6) + (start_m // 10)
            end_col = 2 + ((end_h - 8) * 6) + (end_m // 10)
            
            if start_col < 2: start_col = 2
            if end_col > 62: end_col = 62
        except Exception as e:
            start_col = 2
            end_col = 14 
            
        if sub.name not in subject_colors:
            h = random.randint(0, 360)
            subject_colors[sub.name] = f"hsl({h}, 80%, 85%)"
            
        processed_subjects.append({
            'id': sub.id, 'name': sub.name, 'day': sub.day,
            'time': sub.time, 'room': sub.room,
            'start_col': start_col, 'end_col': end_col,
            'bg_color': subject_colors[sub.name]
        })
        
    # 2. ลอจิกแยกชั้น (Row) อัตโนมัติเมื่อวิชาเวลาทับซ้อนกัน
    current_row = 2
    day_labels = []
    
    for day_data in days_info:
        day_th = day_data["th"]
        # ดึงวิชาของวันนี้มาเรียงตามเวลาเริ่ม
        day_subs = [s for s in processed_subjects if s['day'] == day_th]
        day_subs.sort(key=lambda x: x['start_col'])
        
        tracks = [] # แถวย่อยภายใน 1 วัน
        for sub in day_subs:
            placed = False
            for i, track in enumerate(tracks):
                overlap = False
                for existing_sub in track:
                    # ถ้าเวลาคาบเกี่ยวกัน ถือว่าทับกัน!
                    if sub['start_col'] < existing_sub['end_col'] and sub['end_col'] > existing_sub['start_col']:
                        overlap = True
                        break
                if not overlap:
                    sub['row'] = current_row + i
                    track.append(sub)
                    placed = True
                    break
            
            if not placed:
                # ถ้าทับหมดทุกชั้น ให้งอกชั้นใหม่ขึ้นมา
                sub['row'] = current_row + len(tracks)
                tracks.append([sub])
                
        # วันนี้ใช้ไปกี่แถว (อย่างน้อยต้องมี 1 แถว เพื่อวาดตารางเปล่าๆ)
        rows_used = max(1, len(tracks))
        
        day_labels.append({
            'name_en': day_data["en"],
            'start_row': current_row,
            'span': rows_used
        })
        
        current_row += rows_used
        schedule_data.extend(day_subs)
        
    total_rows = current_row - 2 # จำนวนแถวทั้งหมดที่ต้องให้ CSS Grid วาด

    return render_template('schedule.html', 
                           schedule_data=schedule_data, 
                           day_labels=day_labels, 
                           total_rows=total_rows)

# ลบวิชาเรียน
@app.route('/delete_class/<int:id>')
def delete_class(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('schedule'))

# --- ส่วนของหน้าเพิ่มวิชาเรียน ---
@app.route('/add_class', methods=['GET', 'POST'])
def add_class():
    if request.method == 'POST':
        # รับค่าเวลาเริ่มและเวลาเลิกจากฟอร์ม HTML
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        
        # นำเวลามาต่อกันให้อยู่ในรูปแบบ "HH:MM - HH:MM" เพื่อให้ตารางเรียนอ่านค่าได้เหมือนเดิม
        combined_time = f"{start_time} - {end_time}"
        
        new_subject = Subject(
            name=request.form['name'],
            day=request.form['day'],
            time=combined_time,
            room=request.form['room']
        )
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('schedule'))
        
    return render_template('add_class.html')

# --- ระบบสมาชิก (Auth) ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(
            username=request.form['username'],
            password=request.form['password'] # ของจริงควรเข้ารหัสพาสเวิร์ด แต่นี่เป็นงานส่งอาจารย์แบบด่วน เอาแบบนี้ไปก่อนครับ
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # ค้นหา User ในฐานข้อมูล
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user:
            session['username'] = user.username # จำชื่อผู้ใช้ลงใน session
            return redirect(url_for('profile'))
        else:
            return "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง! <a href='/login'>ลองใหม่</a>"
            
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login')) # ถ้ายังไม่ล็อกอิน ให้เด้งไปหน้า login
    return render_template('profile.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None) # ลบข้อมูลออกจาก session
    return redirect(url_for('home'))

if __name__ == '__main__':
    # สร้างไฟล์ฐานข้อมูลอัตโนมัติก่อนรันแอป
    with app.app_context():
        db.create_all()
    app.run(debug=True)