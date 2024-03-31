"""empty message

Revision ID: 9f467d96ed74
Revises: a97f6cef34eb
Create Date: 2024-03-28 21:17:52.148291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f467d96ed74'
down_revision = 'a97f6cef34eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('county', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('town', sa.String(length=15), nullable=True))
        batch_op.add_column(sa.Column('dob', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('gender', sa.String(length=7), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('address', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('address')
        batch_op.drop_column('created_at')
        batch_op.drop_column('gender')
        batch_op.drop_column('dob')
        batch_op.drop_column('town')
        batch_op.drop_column('county')
        batch_op.drop_column('phone')

    # ### end Alembic commands ###
