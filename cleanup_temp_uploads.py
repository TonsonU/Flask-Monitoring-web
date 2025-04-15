import os
import time
from datetime import datetime, timedelta
from flask import current_app

# สร้างสคริปต์หรือ background task (เช่น cron job หรือ Celery task) เพื่อลบไฟล์ในโฟลเดอร์ static/temp_uploads ที่มีอายุมากกว่าเวลาที่กำหนด

def cleanup_temp_uploads():
    # กำหนดเวลาที่ไฟล์ถือว่าเก่า เช่น 24 ชั่วโมง
    expiration_time = timedelta(hours=24)
    temp_folder = os.path.join(current_app.root_path, 'static', 'temp_uploads')
    now = datetime.now()
    if os.path.exists(temp_folder):
        for filename in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, filename)
            if os.path.isfile(file_path):
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_mtime > expiration_time:
                    try:
                        os.remove(file_path)
                        print(f"Deleted expired temp file: {file_path}")
                    except Exception as e:
                        print(f"Error deleting temp file {file_path}: {e}")

if __name__ == '__main__':
    cleanup_temp_uploads()
