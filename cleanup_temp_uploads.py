# cleanup_temp_uploads.py
import os
from datetime import datetime, timedelta

def cleanup_temp_uploads():
    expiration_time = timedelta(hours=24)
    # ระบุ path ของโฟลเดอร์บนระบบไฟล์โดยตรง
    temp_folder = '/home/signalling/Desktop/Flask-Monitoring-web-feature-docker1/app/static/temp_uploads'  # แก้ path ให้ตรงกับของคุณ
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
