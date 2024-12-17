Update Rev.00
1. การ Confirm การ Delete Work ในหน้า Index.html
2. ตารางแสดงผลในหน้า Index.html รูปแบบใหม่
3. Create Work ไม่ต้องกรอก Username ในหน้า create.html
4. ตอน Edit Work ไม่ให้แก้ไข Username ในหน้า edit.html
5. เพิ่มหน้า closed.html แยกหน้า Index แสดงเฉพาะ Work ที่ Open และหน้า Closed แสดงเฉพาะ Work ที่ Closed

- feature/organization file
config.py: เก็บการตั้งค่าทั้งหมดของแอป
models.py: เก็บโมเดลที่เกี่ยวข้องกับฐานข้อมูล
forms.py: เก็บฟอร์มทั้งหมดที่ใช้ในแอป
routes.py: เก็บเส้นทางของแอป (Routes)
app.py: เป็นไฟล์หลักที่รวมทุกอย่าง
backup_app.py: backup ไฟล์ app เก่า