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

# --- สร้างตารางเก็บข้อมูลผู้ใช้งาน (User) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

# Route หน้าแรก (Landing Page)
@app.route('/')
def home():
    return render_template('index.html')

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
    
    schedule_data = []
    subject_colors = {} # สร้าง Dictionary เพื่อจำว่าวิชาไหน ใช้สีอะไร
    
    for sub in subjects:
        # 1. กำหนดแถว (Row)
        days_map = {
            "วันจันทร์": 2, "วันอังคาร": 3, "วันพุธ": 4, 
            "วันพฤหัสบดี": 5, "วันศุกร์": 6, "วันเสาร์": 7, "วันอาทิตย์": 8
        }
        row = days_map.get(sub.day, 2)
        
        # 2. กำหนดคอลัมน์ (Column) ตามเวลา
        try:
            start_t, end_t = sub.time.split('-')
            start_h = int(start_t.split(':')[0].strip())
            end_h = int(end_t.split(':')[0].strip())
            start_col = start_h - 8 + 2
            end_col = end_h - 8 + 2
        except:
            start_col = 2
            end_col = 4 
            
        # 3. ลอจิกสุ่มสี (วิชาเดียวกันต้องได้สีเดียวกัน)
        if sub.name not in subject_colors:
            # ถ้าวิชานี้ยังไม่มีสี ให้สุ่มสีพาสเทลใหม่ (ใช้ระบบสี HSL เพื่อให้สีอ่อนๆ สบายตา)
            h = random.randint(0, 360) # สุ่มเฉดสี
            subject_colors[sub.name] = f"hsl({h}, 80%, 85%)" # ล็อกความสดและความสว่างให้เป็นพาสเทล
            
        schedule_data.append({
            'id': sub.id,
            'name': sub.name,
            'day': sub.day,
            'time': sub.time,
            'row': row,
            'start_col': start_col,
            'end_col': end_col,
            'bg_color': subject_colors[sub.name] # ดึงสีที่สุ่มไว้มาใช้
        })
        
    return render_template('schedule.html', schedule_data=schedule_data)

# ลบวิชาเรียน
@app.route('/delete_class/<int:id>')
def delete_class(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('schedule'))

@app.route('/add_class', methods=['GET', 'POST'])
def add_class():
    if request.method == 'POST':
        new_subject = Subject(
            name=request.form['name'],
            day=request.form['day'],
            time=request.form['time']
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