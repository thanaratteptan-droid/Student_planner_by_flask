from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

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

if __name__ == '__main__':
    # สร้างไฟล์ฐานข้อมูลอัตโนมัติก่อนรันแอป
    with app.app_context():
        db.create_all()
    app.run(debug=True)