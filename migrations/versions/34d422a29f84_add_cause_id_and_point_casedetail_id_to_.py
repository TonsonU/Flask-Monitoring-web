from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '34d422a29f84'
down_revision = '4cfec45bcf8f'
branch_labels = None
depends_on = None


def upgrade():
    # เช็คว่าตาราง 'cause' มีอยู่หรือยัง
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    if 'cause' not in inspector.get_table_names():
        op.create_table(
            'cause',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )

    if 'point_case_detail' not in inspector.get_table_names():
        op.create_table(
            'point_case_detail',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )

    with op.batch_alter_table('work', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cause_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('point_casedetail_id', sa.Integer(), nullable=True))

        batch_op.create_foreign_key(
            "fk_work_cause_id", "cause", ["cause_id"], ["id"]
        )
        batch_op.create_foreign_key(
            "fk_work_point_casedetail_id", "point_case_detail", ["point_casedetail_id"], ["id"]
        )


def downgrade():
    with op.batch_alter_table('work', schema=None) as batch_op:
        batch_op.drop_constraint("fk_work_cause_id", type_="foreignkey")
        batch_op.drop_constraint("fk_work_point_casedetail_id", type_="foreignkey")

        batch_op.drop_column('point_casedetail_id')
        batch_op.drop_column('cause_id')

    # ลบตารางเฉพาะที่มีอยู่จริง
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    if 'point_case_detail' in inspector.get_table_names():
        op.drop_table('point_case_detail')

    if 'cause' in inspector.get_table_names():
        op.drop_table('cause')
