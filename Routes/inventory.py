from flask import Blueprint, render_template,request, url_for, flash, redirect
from flask_login import login_required,current_user
from models import DeviceName, DeviceType, SerialNumberHistory, ForceDataHistory, MacAddressHistory, ModuleHistory, db
from sqlalchemy import or_
from forms import EditForceDataForm, EditSerialNumberForm, EditMacAddressForm, EditModuleForm

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory_all')
@login_required
def inventory():
        devices = DeviceName.query.all()
        return render_template("inventory/inventory.html", devices=devices)
    
@inventory_bp.route('/inventory_IL', endpoint='inventory_il')
@login_required
def inventory_il():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'IL').all()
        return render_template("inventory/inventory_il.html", devices=devices)
    
@inventory_bp.route('/inventory_tap', endpoint='inventory_tap')
@login_required
def inventory_tap():
        # กรองข้อมูลเพื่อแสดงเฉพาะ Device Type ที่เป็น TAP
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'TAP').all()
        return render_template("inventory/inventory_tap.html", devices=devices)
    
@inventory_bp.route('/inventory_emp', endpoint='inventory_emp')
@login_required
def inventory_emp():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'EMP').all()
        return render_template("inventory/inventory_emp.html", devices=devices)
    
@inventory_bp.route('/inventory_pid', endpoint='inventory_pid')
@login_required
def inventory_pid():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'PID').all()
        return render_template("inventory/inventory_pid.html", devices=devices)
    
@inventory_bp.route('/inventory_obc', endpoint='inventory_obc')
@login_required
def inventory_obc():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'OBC').all()
        return render_template("inventory/inventory_obc.html", devices=devices)
    
@inventory_bp.route('/inventory_tel', endpoint='inventory_tel')
@login_required
def inventory_tel():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'TEL').all()
        return render_template("inventory/inventory_tel.html", devices=devices)
    
@inventory_bp.route('/inventory_ups', endpoint='inventory_ups')
@login_required
def inventory_ups():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'UPS').all()
        return render_template("inventory/inventory_ups.html", devices=devices)
    
@inventory_bp.route('/inventory_point', endpoint='inventory_point')
@login_required
def inventory_point():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Point').all()
        return render_template("inventory/inventory_point.html", devices=devices)
    
@inventory_bp.route('/inventory_balise', endpoint='inventory_balise')
@login_required
def inventory_balise():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Balise').all()
        return render_template("inventory/inventory_balise.html", devices=devices)
    
@inventory_bp.route('/inventory_mitrac', endpoint='inventory_mitrac')
@login_required
def inventory_mitrac():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Mitrac').all()
        return render_template("inventory/inventory_mitrac.html", devices=devices)
    
@inventory_bp.route('/inventory_pli', endpoint='inventory_pli')
@login_required
def inventory_pli():
        devices = DeviceName.query.join(DeviceType).filter(or_(DeviceType.name == 'PLI', DeviceType.name == 'Depot Area Signal', DeviceType.name == 'Route Indicator') ).all()
        return render_template("inventory/inventory_pli.html", devices=devices)
    
@inventory_bp.route('/inventory_axle', endpoint='inventory_axle')
@login_required
def inventory_axle():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Axle Counter').all()
        return render_template("inventory/inventory_axle.html", devices=devices)
    
@inventory_bp.route('/inventory_trackname', endpoint='inventory_trackname')
@login_required
def inventory_trackname():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Track Name Plate').all()
        return render_template("inventory/inventory_trackname.html", devices=devices)


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

        return render_template('inventory/edit_serial_number.html', form=form, device=device, history=history_records,ref=ref)
    

    # Route สำหรับแก้ไข force_data
@inventory_bp.route('/device/<int:device_id>/edit_force_data', methods=['GET', 'POST'])
@login_required
def edit_force_data(device_id):
        device = DeviceName.query.get_or_404(device_id)
        form = EditForceDataForm(obj=device)

        if form.validate_on_submit():
            plus_before = form.plus_before.data
            minus_before = form.minus_before.data
            plus_after = form.plus_after.data if form.plus_after.data else None
            minus_after = form.minus_after.data if form.minus_after.data else None
            remark = form.remark.data

            # บันทึกประวัติการเปลี่ยนแปลง
            force_data_history = ForceDataHistory(
            device_id=device.id,
            plus_before=plus_before,
            minus_before=minus_before,
            plus_after=plus_after,
            minus_after=minus_after,
            changed_by=current_user.id,
            remark=remark            
            )
            db.session.add(force_data_history)
            # อัปเดตค่า force_data ของ device
            if plus_after is not None and minus_after is not None:
                device.force_data = f"{plus_after}, {minus_after}"                
            else:
                device.force_data = f"{plus_before}, {minus_before}"

            print(f"device.force_data: {device.force_data}")            
                    
            db.session.commit()

            flash('Force Data updated successfully!', 'success')
            
            return redirect(url_for('inventory.edit_force_data', device_id=device.id))
            

        # ดึงประวัติการเปลี่ยนแปลง
        history_force_records = ForceDataHistory.query.filter_by(device_id=device.id).order_by(ForceDataHistory.changed_at.desc()).all()

        return render_template('inventory/edit_force_data.html', form=form, device=device, history=history_force_records)
    

    # Route สำหรับแก้ไข mac_address
@inventory_bp.route('/device/<int:device_id>/edit_mac', methods=['GET', 'POST'])
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

        return render_template('inventory/edit_mac_address.html', form=form, device=device, history=history_records)
    
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
        return render_template('inventory/edit_pli_module.html', form=form, device=device, history=history_records)
