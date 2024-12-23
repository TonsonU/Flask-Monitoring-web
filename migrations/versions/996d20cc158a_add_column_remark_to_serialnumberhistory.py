"""add column remark to SerialNumberHistory

Revision ID: 996d20cc158a
Revises: 98a848a1b2a1
Create Date: 2024-12-22 00:00:33.456850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '996d20cc158a'
down_revision = '98a848a1b2a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('serial_number_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('remark', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('work', schema=None) as batch_op:
        batch_op.alter_column('create_date',
               existing_type=sa.DATETIME(),
               nullable=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)

    with op.batch_alter_table('serial_number_history', schema=None) as batch_op:
        batch_op.drop_column('remark')

    with op.batch_alter_table('device_name', schema=None) as batch_op:
        batch_op.alter_column('bound',
               existing_type=sa.VARCHAR(length=100),
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
