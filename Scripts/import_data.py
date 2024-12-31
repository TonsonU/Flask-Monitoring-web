####################################################
# Flask Monitoring Web
#
# 
# Project : Python, Flask, MySQLite, Bootstrap
# Author  : Thanapoom Sukarin, Tonson Ubonsri
# Modifier: 
# Version : 
# Date    : Dec 01, 2024
#
####################################################

# scripts/import_data.py

import sys
import os
import pandas as pd

# เพิ่มรูทโปรเจกต์ลงใน PYTHONPATH เพื่อให้สามารถนำเข้าโมดูลได้
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import app, db
from models import Line, Location, DeviceType, DeviceName



def add_lines_from_excel(file_path):
    df = pd.read_excel(file_path)
    
    for _, row in df.iterrows():
        line_id = row.get('id', None)
        line_name = row.get('name', None)
        
        # สร้างอ็อบเจ็กต์ Line ใหม่
        line = Line(
            id=line_id,
            name=line_name
        )
        # เพิ่มลงใน session
        db.session.add(line)

    # commit เมื่อวนลูปจบ
    db.session.commit()
    print("Add Line Success")

def add_locations_from_excel(file_path):
    df = pd.read_excel(file_path)
    
    for index, row in df.iterrows():
        row_id = row.get('id', None)
        row_name = row.get('name', None)
        row_line_id = row.get('line_id', None)

        # สร้าง Location จากข้อมูลแต่ละแถว
        location = Location(
            id=row_id,
            name=row_name,
            line_id=row_line_id
        )
        db.session.add(location)

    db.session.commit()
    print("Add Location Success")

def add_device_types_from_excel(file_path):
    df = pd.read_excel(file_path)
    
    for _, row in df.iterrows():
        # อ่านข้อมูลสามคอลัมน์หลัก
        device_type_id = row.get('id', None)
        device_type_name = row.get('name', None)
        device_type_line_id = row.get('line_id', None)
        
        # สร้าง DeviceType ใหม่ (สมมติว่ามีฟิลด์ id, name, line_id)
        device_type = DeviceType(
            id=device_type_id,
            name=device_type_name,
            line_id=device_type_line_id
        )
        db.session.add(device_type)
    
    db.session.commit()
    print("Add DeviceType Success")


def add_device_names_from_excel(file_path):
    df = pd.read_excel(file_path)
    
    for _, row in df.iterrows():
        device_id = row.get('id', None)
        device_name = row.get('name', None)
        device_type_id = row.get('device_type_id', None)
        location_id = row.get('location_id', None)
        bound = row.get('bound', None)
        inandout = row.get('inandout', None)
        serial_number = row.get('serial_number', None)
        
        device = DeviceName(
            id=device_id,
            name=device_name,
            device_type_id=device_type_id,
            location_id=location_id,
            bound=bound,
            inandout=inandout,
            serial_number=serial_number
        )
        db.session.add(device)
    
    db.session.commit()
    print("Add DeviceName Success")


def main():
    with app.app_context():
        try:
            
            add_lines_from_excel('data/line.xlsx')
            add_locations_from_excel('data/location.xlsx')
            add_device_types_from_excel('data/device_type.xlsx')
            add_device_names_from_excel('data/device_name rev01.xlsx')

            print("Import Data from Excel Success")
        except Exception as e:
            db.session.rollback()
            print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
