# ใช้ Python 3.10 เป็น base image
FROM python:3.10-slim

# ตั้งค่า environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# สร้าง directory สำหรับ app
WORKDIR /app

# คัดลอกและติดตั้ง dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอก source code ทั้งหมด
COPY . /app/

# เปิดพอร์ต 5000
EXPOSE 5000

# รันแอปด้วย gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]