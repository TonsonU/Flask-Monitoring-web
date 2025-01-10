####################################################
# Flask Monitoring Web
#
# 
# Project : Python, Flask, MySQLite, Bootstrap
# Author  : Thanapoom Sukarin
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


def add_lines_from_excel(file_path, sheet_name='Line'):
    """
    อ่านข้อมูลจาก Sheet ชื่อ 'line' แล้วบันทึกลงตาราง Line
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    for _, row in df.iterrows():
        line_id = row.get('ID', None)
        line_name = row.get('Name', None)
        
        line = Line(
            id=line_id,
            name=line_name
        )
        db.session.add(line)

    db.session.commit()
    print("Add Line Success")

def add_locations_from_excel(file_path, sheet_name='Location'):
    """
    อ่านข้อมูลจาก Sheet ชื่อ 'location' แล้วบันทึกลงตาราง Location
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    for _, row in df.iterrows():
        row_id = row.get('ID', None)
        row_name = row.get('Name', None)
        row_line_id = row.get('Line_ID', None)

        location = Location(
            id=row_id,
            name=row_name,
            line_id=row_line_id
        )
        db.session.add(location)

    db.session.commit()
    print("Add Location Success")

def add_device_types_from_excel(file_path, sheet_name='Device_Type'):
    """
    อ่านข้อมูลจาก Sheet ชื่อ 'device_type' แล้วบันทึกลงตาราง DeviceType
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    for _, row in df.iterrows():
        device_type_id = row.get('ID', None)
        device_type_name = row.get('Name', None)
        device_type_line_id = row.get('Line_ID', None)
        
        device_type = DeviceType(
            id=device_type_id,
            name=device_type_name,
            line_id=device_type_line_id
        )
        db.session.add(device_type)
    
    db.session.commit()
    print("Add DeviceType Success")

def add_device_names_from_excel(file_path, sheet_name='Device_Name'):
    """
    อ่านข้อมูลจาก Sheet ชื่อ 'device_name' แล้วบันทึกลงตาราง DeviceName
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    for _, row in df.iterrows():
        device_id = row.get('ID', None)
        device_name = row.get('Name', None)
        device_type_id = row.get('Device_Type_ID', None)
        location_id = row.get('Location_ID', None)
        bound = row.get('Bound', None)
        inandout = row.get('InandOut', None)
        serial_number = row.get('Serial_Number', None)
        
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
            # หากไฟล์ Excel รวมชื่อ 'data.xlsx'
            excel_file_path = 'data/device_name rev11.xlsx'
            
            add_lines_from_excel(excel_file_path, sheet_name='Line')
            add_locations_from_excel(excel_file_path, sheet_name='Location')
            add_device_types_from_excel(excel_file_path, sheet_name='Device_Type')
            add_device_names_from_excel(excel_file_path, sheet_name='Device_Name')

            print("Import Data from Excel Success")
        except Exception as e:
            db.session.rollback()
            print(f"Error: {str(e)}")


if __name__ == '__main__':
    main()

