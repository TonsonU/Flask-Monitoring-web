# ใช้ภาพพื้นฐานของ Python
FROM python:3.10

# ตั้งค่าตัวแปรสภาพแวดล้อม
ENV PYTHONUNBUFFERED 1

# กำหนด working directory ใน container
WORKDIR /app

# คัดลอกไฟล์ requirements.txt ไปยังไดเรกทอรีการทำงาน
COPY requirements.txt /app/

# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกไฟล์โปรเจคทั้งหมดไปยังไดเรกทอรีการทำงาน
COPY . /app/

# เปิดพอร์ต 5000
EXPOSE 5000

# กำหนดคำสั่งให้ Flask รันผ่าน Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]