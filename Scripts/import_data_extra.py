import sys
import os
import pandas as pd

# เพิ่มรูทโปรเจกต์ลงใน PYTHONPATH เพื่อให้สามารถนำเข้าโมดูลได้
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import app, db
from models import Cause, PointCaseDetail


def add_cause_from_excel(file_path, sheet_name='Cause'):
    """
    อ่านข้อมูลจาก Sheet 'Cause' แล้วบันทึกลงตาราง Cause
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        causes_to_add = []
        
        for _, row in df.iterrows():
            cause_id = row.get('ID')
            cause_name = row.get('Name')

            # ถ้า name เป็น None หรือว่างเปล่า ข้ามไป
            if not cause_name or pd.isna(cause_name):
                print(f"⚠️ Skipping cause with missing name (ID: {cause_id})")
                continue

            # ตรวจสอบว่ามีอยู่แล้วในฐานข้อมูลหรือไม่
            existing_cause = db.session.query(Cause).filter_by(name=cause_name).first()
            if existing_cause:
                print(f"⚠️ Skipping duplicate Cause: {cause_name}")
                continue

            cause = Cause(id=cause_id, name=cause_name)
            causes_to_add.append(cause)

        if causes_to_add:
            db.session.bulk_save_objects(causes_to_add)
            db.session.commit()
            print("✅ Add Cause Success")
        else:
            print("⚠️ No new Cause data to add.")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in add_cause_from_excel: {str(e)}")


def add_point_case_detail_from_excel(file_path, sheet_name='Point_Case_Detail'):
    """
    อ่านข้อมูลจาก Sheet 'Point_Case_Detail' แล้วบันทึกลงตาราง PointCaseDetail
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        point_case_details_to_add = []
        
        for _, row in df.iterrows():
            point_id = row.get('ID')
            point_name = row.get('Name')

            # ถ้า name เป็น None หรือว่างเปล่า ข้ามไป
            if not point_name or pd.isna(point_name):
                print(f"⚠️ Skipping Point Case Detail with missing name (ID: {point_id})")
                continue

            # ตรวจสอบว่ามีอยู่แล้วในฐานข้อมูลหรือไม่
            existing_point = db.session.query(PointCaseDetail).filter_by(name=point_name).first()
            if existing_point:
                print(f"⚠️ Skipping duplicate Point Case Detail: {point_name}")
                continue

            point_case_detail = PointCaseDetail(id=point_id, name=point_name)
            point_case_details_to_add.append(point_case_detail)

        if point_case_details_to_add:
            db.session.bulk_save_objects(point_case_details_to_add)
            db.session.commit()
            print("✅ Add PointCaseDetail Success")
        else:
            print("⚠️ No new PointCaseDetail data to add.")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in add_point_case_detail_from_excel: {str(e)}")


def main():
    with app.app_context():
        try:
            excel_file_path = 'data/Cause.xlsx'

            # ดึงข้อมูล Cause และ Point Case Detail
            add_cause_from_excel(excel_file_path, sheet_name='Cause')
            add_point_case_detail_from_excel(excel_file_path, sheet_name='Point_Case_Detail')

            print("✅ Import Data from Excel Success")
        except Exception as e:
            print(f"❌ Error in main(): {str(e)}")


if __name__ == '__main__':
    main()
