"""Fix backref name conflict in ForceDataHistory

Revision ID: aaf32dbf8f5c
Revises: 71377a3fa4d9
Create Date: 2025-01-13 14:25:44.064406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aaf32dbf8f5c'
down_revision = '71377a3fa4d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('force_data_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('plus_before', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('minus_before', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('plus_after', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('minus_after', sa.Integer(), nullable=True))
        batch_op.drop_column('Minus_Before')
        batch_op.drop_column('Minus_After')
        batch_op.drop_column('Plus_Before')
        batch_op.drop_column('Plus_After')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('force_data_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('Plus_After', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('Plus_Before', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('Minus_After', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('Minus_Before', sa.INTEGER(), nullable=False))
        batch_op.drop_column('minus_after')
        batch_op.drop_column('plus_after')
        batch_op.drop_column('minus_before')
        batch_op.drop_column('plus_before')

    # ### end Alembic commands ###
