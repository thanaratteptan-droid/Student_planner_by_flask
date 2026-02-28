# Student_planner_by_flask

# 🎓 Student Planner - Ultimate Task & Schedule Manager

![Student Planner Banner](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)

**Student Planner** คือ Web Application อัจฉริยะที่ออกแบบมาเพื่อช่วยนักศึกษาจัดการชีวิตการเรียนให้ง่ายและมีประสิทธิภาพมากขึ้น ไม่ใช่แค่การจด To-Do List ธรรมดา แต่มาพร้อมฟีเจอร์ระดับ Enterprise เช่น ระบบ AI ช่วยแตกย่อยงาน, Global Pomodoro Timer, และตารางเรียนที่สามารถแคปเจอร์เป็นรูปภาพได้!

---

## ฟีเจอร์เด่น (Key Features)

### Smart Task Management
* **CRUD Operations:** เพิ่ม แก้ไข ลบ และอัปเดตสถานะงานได้อย่างสมบูรณ์
* **Priority Levels:** จัดระดับความสำคัญของงาน (🔥 ด่วนมาก, ⚡ ปานกลาง, 🍃 ชิลๆ) พร้อมป้ายสีแยกชัดเจน
* **Live Search:** ค้นหางานแบบ Real-time โดยไม่ต้องรีเฟรชหน้าเว็บ
* **Success Progress:** หลอดพลังบอกเปอร์เซ็นต์ความสำเร็จ พร้อมแอนิเมชันจุดพลุ (Confetti) เมื่อเคลียร์งานครบ 100%

###  Productivity Tools (ตัวช่วยเพิ่มความโปร)
* **Simulated AI Task Breakdown:** ผู้ช่วย AI จำลองที่ช่วยวิเคราะห์และแตกย่อยสเกลงานใหญ่ๆ ให้ออกมาเป็น Sub-tasks ที่ทำตามได้ง่าย (พร้อม Loading Effect สุดเนียน)
* **🍅 Global Pomodoro Timer:** นาฬิกาจับเวลาโฟกัส (25/5 นาที) ที่ทำงานต่อเนื่องข้ามหน้าเว็บ (Background Sync) ผ่าน `localStorage` พร้อมป้ายแสดงสถานะบน Navbar
* **Lofi Study Player:** วิดเจ็ตเครื่องเล่นเพลง Spotify Lofi Girl ฝังอยู่ข้างหน้าปัด Pomodoro เอาไว้เปิดฟังตอนปั่นงาน

###  Interactive Schedule & Calendar
* **FullCalendar View:** ปฏิทินแสดงวันกำหนดส่งงาน ดึงข้อมูลจากฐานข้อมูลมาแสดงผลพร้อมแยกสีตามความสำคัญ (รองรับการคลิกเพื่อแก้ไขงาน)
* **Smart Timetable:** ตารางเรียนแบบ CSS Grid อัตโนมัติ สวยงาม รองรับเอฟเฟกต์ Glassmorphism
* **One-Click Copy:** ปุ่มคัดลอกข้อมูลวิชาเรียนเดิมไปสร้างช่องใหม่ได้ทันทีผ่าน `sessionStorage`
* **Image Export:** สามารถแคปเจอร์หน้าตารางเรียนเป็นไฟล์ `.png` โหลดลงเครื่องได้ทันทีด้วย `html2canvas`

###  UI/UX Design
* **Modern Relational UI:** ดีไซน์การ์ดโค้งมน ดูสะอาดตา ทันสมัย
* **Dark Mode 100%:** รองรับโหมดมืดเต็มรูปแบบ (รวมถึงตารางเรียน ปฏิทิน และ Popup)
* **SweetAlert2:** เปลี่ยน Popup แจ้งเตือนและยืนยันการลบให้สวยงามและดูแพง
* **Custom 404 Page:** หน้าจอแจ้งเตือน Error 404 สไตล์มินิมอลสุดเท่

---

## เทคโนโลยีที่ใช้ (Tech Stack)

* **Backend:** Python, Flask
* **Database:** SQLite (ผ่าน Flask-SQLAlchemy)
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
* **Framework:** Bootstrap 5.3
* **Libraries/APIs:** 
    * [FullCalendar.js](https://fullcalendar.io/) (ปฏิทินงาน)
    * [SweetAlert2](https://sweetalert2.github.io/) (UI Popups)
    * [Canvas Confetti](https://www.kirilv.com/canvas-confetti/) (แอนิเมชันฉลองความสำเร็จ)
    * [html2canvas](https://html2canvas.hertzen.com/) (แคปรูปตารางเรียน)

---

## วิธีการติดตั้งและรันโปรเจกต์ (How to Run)

1. **Clone Repository:**
   ```bash
   git clone https://github.com/thanaratteptan-droid/Student_planner_by_flask
   cd Student_planner_by_flask/student-planner
   python -m streamlit run app.py

