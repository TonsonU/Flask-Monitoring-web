"""edit modal work

Revision ID: 67a538fc35e9
Revises: 
Create Date: 2024-12-18 21:27:15.137081

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67a538fc35e9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('work')

    op.create_table(
        'work',
        sa.Column('number', sa.Integer(), nullable=False, autoincrement=True),  # เลข 6 หลัก รันอัตโนมัติ
        sa.Column('create_date', sa.DateTime(), nullable=False, default=sa.func.now()),  # วันที่และเวลา สร้างอัตโนมัติ
        sa.Column('work_order', sa.String(length=50), nullable=False),  # Work Order
        sa.Column('line_id', sa.Integer(), nullable=True),  # ForeignKey เชื่อมกับตาราง 'line'
        sa.Column('location_id', sa.Integer(), nullable=True),  # ForeignKey เชื่อมกับตาราง 'location'
        sa.Column('device_type_id', sa.Integer(), nullable=True),  # ForeignKey เชื่อมกับตาราง 'device_type'
        sa.Column('device_name_id', sa.Integer(), nullable=True),  # ForeignKey เชื่อมกับตาราง 'device_name'
        sa.Column('description', sa.Text(), nullable=False),  # รายละเอียด
        sa.Column('report_by', sa.String(length=50), nullable=False),  # ผู้รายงาน
        sa.Column('status', sa.String(length=20), nullable=False, default='open'),  # สถานะ (ค่าเริ่มต้น: open)
        sa.Column('action', sa.Text(), nullable=True),  # รายละเอียดของการดำเนินการ
        sa.Column('link', sa.String(length=255), nullable=True),  # URL ของไฟล์

        sa.ForeignKeyConstraint(['line_id'], ['line.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['location.id'], ),
        sa.ForeignKeyConstraint(['device_type_id'], ['device_type.id'], ),
        sa.ForeignKeyConstraint(['device_name_id'], ['device_name.id'], ),

        sa.PrimaryKeyConstraint('number')
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('work', schema=None) as batch_op:
        batch_op.add_column(sa.Column('equipment', sa.VARCHAR(length=50), nullable=False))
        batch_op.add_column(sa.Column('location', sa.VARCHAR(length=50), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('device_name_id')
        batch_op.drop_column('device_type_id')
        batch_op.drop_column('location_id')
        batch_op.drop_column('line_id')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)

    op.create_table('_alembic_tmp_user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=50), nullable=False),
    sa.Column('password', sa.VARCHAR(length=255), nullable=False),
    sa.Column('role', sa.VARCHAR(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###
