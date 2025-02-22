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

from flask import Blueprint, render_template,request, url_for, flash, redirect, jsonify, current_app
from flask_login import login_required,current_user
from app.models import DeviceName, DeviceType, SerialNumberHistory, ForceDataHistory, MacAddressHistory, ModuleHistory, db
from sqlalchemy import or_
from .forms import EditForceDataForm, EditSerialNumberForm, EditMacAddressForm, EditModuleForm
from app.extensions import db
from . import inventory_bp

@inventory_bp.route('/inventory_all')
@login_required
def inventory():
        devices = DeviceName.query.all()
        return render_template("inventory.html", devices=devices)
    
@inventory_bp.route('/inventory_IL', endpoint='inventory_il')
@login_required
def inventory_il():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'IL').all()
        return render_template("inventory_il.html", devices=devices)
    
@inventory_bp.route('/inventory_tap', endpoint='inventory_tap')
@login_required
def inventory_tap():
        # กรองข้อมูลเพื่อแสดงเฉพาะ Device Type ที่เป็น TAP
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'TAP').all()
        return render_template("inventory_tap.html", devices=devices)
    
@inventory_bp.route('/inventory_emp', endpoint='inventory_emp')
@login_required
def inventory_emp():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'EMP').all()
        return render_template("inventory_emp.html", devices=devices)
    
@inventory_bp.route('/inventory_pid', endpoint='inventory_pid')
@login_required
def inventory_pid():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'PID').all()
        return render_template("inventory_pid.html", devices=devices)
    
@inventory_bp.route('/inventory_obc', endpoint='inventory_obc')
@login_required
def inventory_obc():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'OBC').all()
        return render_template("inventory_obc.html", devices=devices)
    
@inventory_bp.route('/inventory_tel', endpoint='inventory_tel')
@login_required
def inventory_tel():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'TEL').all()
        return render_template("inventory_tel.html", devices=devices)
    
@inventory_bp.route('/inventory_ups', endpoint='inventory_ups')
@login_required
def inventory_ups():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'UPS').all()
        return render_template("inventory_ups.html", devices=devices)
    
@inventory_bp.route('/inventory_point', endpoint='inventory_point')
@login_required
def inventory_point():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Point').all()
        force_data_history = {device.id: ForceDataHistory.query.filter_by(device_id=device.id).order_by(ForceDataHistory.changed_at.desc()).first() for device in devices}

        # อัปเดตค่า force_data ของ device จาก ForceDataHistory
        for device in devices:
            if force_data_history[device.id]:
                force_values = [
                    str(force_data_history[device.id].plus_before),
                    str(force_data_history[device.id].minus_before),
                    str(force_data_history[device.id].plus_after),
                    str(force_data_history[device.id].minus_after)
                ]
                device.force_data = ", ".join([value for value in force_values if value != 'None'])



        return render_template("inventory_point.html", devices=devices, force_data_history=force_data_history)
    
@inventory_bp.route('/inventory_balise', endpoint='inventory_balise')
@login_required
def inventory_balise():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Balise').all()
        return render_template("inventory_balise.html", devices=devices)
    
@inventory_bp.route('/inventory_mitrac', endpoint='inventory_mitrac')
@login_required
def inventory_mitrac():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Mitrac').all()
        return render_template("inventory_mitrac.html", devices=devices)
    
@inventory_bp.route('/inventory_pli', endpoint='inventory_pli')
@login_required
def inventory_pli():
        devices = DeviceName.query.join(DeviceType).filter(or_(DeviceType.name == 'PLI', DeviceType.name == 'Depot Area Signal', DeviceType.name == 'Route Indicator') ).all()
        return render_template("inventory_pli.html", devices=devices)
    
@inventory_bp.route('/inventory_axle', endpoint='inventory_axle')
@login_required
def inventory_axle():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Axle Counter').all()
        return render_template("inventory_axle.html", devices=devices)
    
@inventory_bp.route('/inventory_trackname', endpoint='inventory_trackname')
@login_required
def inventory_trackname():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Track Name Plate').all()
        return render_template("inventory_trackname.html", devices=devices)


    # Route สำหรับแก้ไข serial_number
@inventory_bp.route('/device/<int:device_id>/edit_serial', methods=['GET', 'POST'])
@login_required
def edit_serial_number(device_id):
        device = DeviceName.query.get_or_404(device_id)
        ref = request.args.get('ref', url_for('inventory.inventory'))  # รับค่า ref หรือใช้ default_page
        form = EditSerialNumberForm(obj=device)

        if form.validate_on_submit():
            old_serial = device.serial_number
            new_serial = form.serial_number.data
            remark = form.remark.data  # ใช้ฟิลด์จากฟอร์มตรงๆ

            if old_serial != new_serial:
                # บันทึกประวัติการเปลี่ยนแปลง
                history = SerialNumberHistory(
                    device_id=device.id,
                    old_serial_number=old_serial,
                    new_serial_number=new_serial,
                    changed_by=current_user.id,
                    remark=remark  # บันทึก remark
                )
                db.session.add(history)

                # อัปเดต serial_number
                device.serial_number = new_serial
                db.session.commit()

                flash('Serial Number updated successfully!', 'success')
                #return redirect(ref)  # เปลี่ยนเป็น 'inventory'
            else:
                flash('No changes detected.', 'info')
                #return redirect(ref)  # เปลี่ยนเป็น 'inventory'

        # ดึงประวัติการเปลี่ยนแปลง
        history_records = SerialNumberHistory.query.filter_by(device_id=device.id).order_by(SerialNumberHistory.changed_at.desc()).all()

        return render_template('edit_serial_number.html', form=form, device=device, history=history_records,ref=ref)
    


# Route สำหรับแก้ไข force_data
@inventory_bp.route('/force_id/<int:device_id>/edit_force_data', methods=['GET', 'POST'])
@login_required
def edit_force_data(device_id):
        device = DeviceName.query.get_or_404(device_id)
        form = EditForceDataForm(obj=device)

        if form.validate_on_submit():
            try:
                plus_before = form.plus_before.data
                minus_before = form.minus_before.data
                plus_after = form.plus_after.data if form.plus_after.data else None
                minus_after = form.minus_after.data if form.minus_after.data else None
                remark = form.remark.data

                # ตั้งค่า Timezone เป็น Asia/Bangkok
                bangkok_tz = pytz.timezone('Asia/Bangkok')
                current_time = datetime.now(bangkok_tz)  # ได้เวลาปัจจุบันเป็นเวลาไทย

                # บันทึกประวัติการเปลี่ยนแปลง
                force_data_history = ForceDataHistory(
                    device_id=device.id,
                    plus_before=plus_before,
                    minus_before=minus_before,
                    plus_after=plus_after,
                    minus_after=minus_after,
                    changed_by=current_user.id,
                    remark=remark,
                    changed_at=current_time,  # บันทึกวันที่และเวลาเป็น Bangkok timezone
                )
                db.session.add(force_data_history)

                # อัปเดตค่า force_data ของ device
                force_values = [str(value) for value in [plus_before, minus_before, plus_after, minus_after] if value is not None]
                device.force_data = ", ".join(force_values)

                print(f"device.force_data: {device.force_data}")

                # บันทึกลงฐานข้อมูล
                db.session.commit()
                flash('Force Data updated successfully!', 'success')

                return redirect(url_for('edit_force_data', device_id=device.id))

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error updating force data: {e}")
                flash('เกิดข้อผิดพลาดในการอัปเดตข้อมูล', 'danger')

        # ดึงประวัติการเปลี่ยนแปลง
        history_force_records = ForceDataHistory.query.filter_by(device_id=device.id).order_by(ForceDataHistory.changed_at.desc()).all()

        return render_template('edit_force_data.html', form=form, device=device, history=history_force_records)


# Route สำหรับแสดงข้อมูล force_data ในรูปแบบกราฟ
@inventory_bp.route('/api/get_force_data/<int:device_id>', methods=['GET'])
@login_required
def get_force_graph_data(device_id):
        try:
                # Query ข้อมูลจากฐานข้อมูล
                records = ForceDataHistory.query.filter_by(device_id=device_id).order_by(ForceDataHistory.changed_at).all()

                if not records:
                        current_app.logger.warning(f"No records found for device_id {device_id}")
                        return jsonify({"error": "No data found"}), 404

                # แปลงข้อมูลจากฐานข้อมูลให้อยู่ในรูปแบบ JSON
                graph_data = {}
                for record in records:
                        edit_date = record.changed_at.strftime('%Y-%m-%d')  # เปลี่ยนวันที่เป็น string
                        if edit_date not in graph_data:
                                graph_data[edit_date] = {
                                'plus_before': 0,
                                'minus_before': 0,
                                'plus_after': 0,
                                'minus_after': 0
                                }
                        
                        # แปลงค่าที่ได้จากฐานข้อมูลให้เป็นตัวเลขก่อน
                        graph_data[edit_date]['plus_before'] += int(record.plus_before or 0)
                        graph_data[edit_date]['minus_before'] += int(record.minus_before or 0)
                        graph_data[edit_date]['plus_after'] += int(record.plus_after or 0)
                        graph_data[edit_date]['minus_after'] += int(record.minus_after or 0)

                return jsonify(graph_data)

        except ValueError as e:
                current_app.logger.error(f"Error converting data to int: {e}")
                return jsonify({"error": "Invalid data type in database"}), 500
        except Exception as e:
                current_app.logger.error(f"Error fetching data for device_id {device_id}: {e}")
                return jsonify({"error": "Internal Server Error"}), 500
        
# Route สำหรับลบ force_data
@inventory_bp.route('/delete_force_data/<int:record_id>', methods=['POST'])
@login_required
def delete_force_data(record_id):
        record = ForceDataHistory.query.get_or_404(record_id)

        # ตรวจสอบว่าเป็นเจ้าของข้อมูลหรือไม่
        if record.changed_by != current_user.id:
            flash("คุณไม่มีสิทธิ์ลบข้อมูลนี้", "danger")
            return jsonify({"error": "Unauthorized"}), 403

        try:
            db.session.delete(record)
            db.session.commit()
            flash("ลบข้อมูลสำเร็จ!", "success")
            return jsonify({"success": True}), 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting record {record_id}: {e}")
            return jsonify({"error": "เกิดข้อผิดพลาดในการลบข้อมูล"}), 500


    

    # Route สำหรับแก้ไข mac_address
@inventory_bp.route('/tap_mac_id/<int:device_id>/edit_mac', methods=['GET', 'POST'])
@login_required
def edit_mac_address(device_id):
        device = DeviceName.query.get_or_404(device_id)
        form = EditMacAddressForm(obj=device)

        if form.validate_on_submit():
            old_mac = device.mac_address
            new_mac = form.mac_address.data
            remark = form.remark.data  # ใช้ฟิลด์จากฟอร์มตรงๆ

            if old_mac != new_mac:
                # บันทึกประวัติการเปลี่ยนแปลง
                history = MacAddressHistory(
                    device_id=device.id,
                    old_mac_address=old_mac,
                    new_mac_address=new_mac,
                    changed_by=current_user.id,
                    remark=remark  # บันทึก remark
                )
                db.session.add(history)

                # อัปเดต mac_address
                device.mac_address = new_mac
                db.session.commit()

                flash('MAC Address updated successfully!', 'success')
                return redirect(url_for('inventory.edit_mac_address', device_id=device.id))  # เปลี่ยนเป็น 'inventory'
            else:
                flash('No changes detected.', 'info')
                return redirect(url_for('inventory.edit_mac_address', device_id=device.id))  # เปลี่ยนเป็น 'inventory'

        # ดึงประวัติการเปลี่ยนแปลง
        history_records = MacAddressHistory.query.filter_by(device_id=device.id).order_by(MacAddressHistory.changed_at.desc()).all()

        return render_template('edit_mac_address.html', form=form, device=device, history=history_records)
    
@inventory_bp.route('/device/<int:device_id>/edit_pli_module', methods=['GET', 'POST'])
@login_required
def edit_pli_module(device_id):
        device = DeviceName.query.get_or_404(device_id)
        form = EditModuleForm(obj=device)

        if form.validate_on_submit():
            old_red_module = device.red_module
            old_white_module = device.white_module
            old_yellow_module = device.yellow_module

            new_red_module = form.red_module.data
            new_white_module = form.white_module.data
            new_yellow_module = form.yellow_module.data
            remark = form.remark.data

            if old_red_module != new_red_module or old_white_module != new_white_module or old_yellow_module != new_yellow_module:
                history = ModuleHistory(
                    device_id=device.id,
                    old_red_module=old_red_module,
                    new_red_module=new_red_module,
                    old_white_module=old_white_module,
                    new_white_module=new_white_module,
                    old_yellow_module=old_yellow_module,
                    new_yellow_module=new_yellow_module,
                    changed_by=current_user.id,
                    remark=remark
                )
                db.session.add(history)

                device.red_module = new_red_module
                device.white_module = new_white_module
                device.yellow_module = new_yellow_module
                db.session.commit()

                flash('PLI Module data updated successfully!', 'success')
            else:
                flash('No changes detected.', 'info')

            return redirect(url_for('inventory.edit_pli_module', device_id=device.id))

        history_records = ModuleHistory.query.filter_by(device_id=device.id).order_by(ModuleHistory.changed_at.desc()).all()
        return render_template('edit_pli_module.html', form=form, device=device, history=history_records)
