from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey1234'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planner.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# อัปโหลดรูปภาพ
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # สร้างโฟลเดอร์อัตโนมัติถ้ายังไม่มี

db = SQLAlchemy(app)

# --- Database Models (อัปเดตเพิ่ม user_id เพื่อแยกโปรไฟล์) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    profile_pic = db.Column(db.String(200), nullable=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    due_date = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Pending')
    # ผูก Task กับ User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    day = db.Column(db.String(20))
    time = db.Column(db.String(50))
    room = db.Column(db.String(50))
    # ผูก Subject กับ User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- Helper Function: ดึงข้อมูล User ปัจจุบัน ---
def get_current_user():
    if 'username' in session:
        return User.query.filter_by(username=session['username']).first()
    return None

# --- Routes ---
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user: return redirect(url_for('login')) # ป้องกันคนไม่ล็อกอินแอบเข้า
    
    # ดึงเฉพาะงานของคนที่ล็อกอิน
    tasks = Task.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', tasks=tasks)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    user = get_current_user()
    if not user: return redirect(url_for('login'))

    if request.method == 'POST':
        new_task = Task(
            title=request.form['title'], 
            description=request.form['description'], 
            due_date=request.form['due_date'],
            user_id=user.id # บันทึกว่างานนี้เป็นของใคร
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_task.html')

@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    user = get_current_user()
    if not user: return redirect(url_for('login'))

    # ดึงงานมาแก้ โดยต้องแน่ใจว่าเป็นงานของตัวเองจริงๆ
    task = Task.query.filter_by(id=id, user_id=user.id).first_or_404()
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.due_date = request.form['due_date']
        task.status = request.form['status']
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_task.html', task=task)

@app.route('/delete_task/<int:id>')
def delete_task(id):
    user = get_current_user()
    if not user: return redirect(url_for('login'))

    task = Task.query.filter_by(id=id, user_id=user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/complete_task/<int:id>')
def complete_task(id):
    user = get_current_user()
    if not user: return redirect(url_for('login'))

    task = Task.query.filter_by(id=id, user_id=user.id).first_or_404()
    task.status = 'Done'
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/history')
def history():
    user = get_current_user()
    if not user: return redirect(url_for('login'))

    tasks = Task.query.filter_by(user_id=user.id, status='Done').all()
    return render_template('history.html', tasks=tasks)

# --- ระบบตารางเรียนอัจฉริยะ (แยกตามโปรไฟล์) ---
@app.route('/schedule')
def schedule():
    user = get_current_user()
    if not user: return redirect(url_for('login'))

    # ดึงเฉพาะวิชาเรียนของคนที่ล็อกอินอยู่
    subjects = Subject.query.filter_by(user_id=user.id).all()
    
    days_info = [
        {"th": "วันจันทร์", "en": "Monday"},
        {"th": "วันอังคาร", "en": "Tuesday"},
        {"th": "วันพุธ", "en": "Wednesday"},
        {"th": "วันพฤหัสบดี", "en": "Thursday"},
        {"th": "วันศุกร์", "en": "Friday"},
        {"th": "วันเสาร์", "en": "Saturday"},
        {"th": "วันอาทิตย์", "en": "Sunday"}
    ]
    
    schedule_data = []
    subject_colors = {}
    processed_subjects = []
    
    for sub in subjects:
        try:
            start_t, end_t = sub.time.split('-')
            start_h = int(start_t.split(':')[0].strip())
            start_m = int(start_t.split(':')[1].strip())
            end_h = int(end_t.split(':')[0].strip())
            end_m = int(end_t.split(':')[1].strip())
            
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
        
    current_row = 2
    day_labels = []
    
    for day_data in days_info:
        day_th = day_data["th"]
        day_subs = [s for s in processed_subjects if s['day'] == day_th]
        day_subs.sort(key=lambda x: x['start_col'])
        
        tracks = [] 
        for sub in day_subs:
            placed = False
            for i, track in enumerate(tracks):
                overlap = False
                for existing_sub in track:
                    if sub['start_col'] < existing_sub['end_col'] and sub['end_col'] > existing_sub['start_col']:
                        overlap = True
                        break
                if not overlap:
                    sub['row'] = current_row + i
                    track.append(sub)
                    placed = True
                    break
            
            if not placed:
                sub['row'] = current_row + len(tracks)
                tracks.append([sub])
                
        rows_used = max(1, len(tracks))
        
        day_labels.append({
            'name_en': day_data["en"],
            'start_row': current_row,
            'span': rows_used
        })
        
        current_row += rows_used
        schedule_data.extend(day_subs)
        
    total_rows = current_row - 2

    return render_template('schedule.html', 
                           schedule_data=schedule_data, 
                           day_labels=day_labels, 
                           total_rows=total_rows)

@app.route('/add_class', methods=['GET', 'POST'])
def add_class():
    user = get_current_user()
    if not user: return redirect(url_for('login'))

    if request.method == 'POST':
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        combined_time = f"{start_time} - {end_time}"
        
        new_subject = Subject(
            name=request.form['name'],
            day=request.form['day'],
            time=combined_time,
            room=request.form['room'],
            user_id=user.id # บันทึกว่าวิชานี้เป็นของใคร
        )
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('schedule'))
    return render_template('add_class.html')

@app.route('/delete_class/<int:id>')
def delete_class(id):
    user = get_current_user()
    if not user: return redirect(url_for('login'))

    subject = Subject.query.filter_by(id=id, user_id=user.id).first_or_404()
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('schedule'))

# --- ระบบสมาชิก ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user:
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            return "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง! <a href='/login'>ลองใหม่</a>"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# --- ระบบแก้ไขโปรไฟล์ และอัปโหลดรูป ---
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user = get_current_user()
    if not user: return redirect(url_for('login'))

    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']

        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user and existing_user.id != user.id:
            return "ชื่อผู้ใช้นี้มีคนใช้แล้ว! <a href='/edit_profile'>ลองใหม่</a>"

        # จัดการอัปโหลดรูปโปรไฟล์
        file = request.files.get('profile_pic')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            # ตั้งชื่อไฟล์ใหม่โดยเอา username มานำหน้า เพื่อไม่ให้ชื่อไฟล์ซ้ำกัน
            unique_filename = f"{user.username}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            user.profile_pic = unique_filename # บันทึกชื่อรูปลงฐานข้อมูล

        user.username = new_username
        if new_password: 
            user.password = new_password
        
        db.session.commit()
        session['username'] = user.username 
        
        return redirect(url_for('profile'))
        
    return render_template('edit_profile.html', user=user)

@app.route('/profile')
def profile():
    user = get_current_user() # ดึงข้อมูล user ปัจจุบันจากฐานข้อมูลทั้งก้อน
    if not user:
        return redirect(url_for('login'))
        
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)