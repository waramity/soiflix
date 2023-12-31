"""empty message

Revision ID: 20812356341e
Revises: d8b02371a139
Create Date: 2021-10-11 13:24:30.721647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20812356341e'
down_revision = 'd8b02371a139'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('season', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.String(length=100), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('season', schema=None) as batch_op:
        batch_op.drop_column('image')

    # ### end Alembic commands ###
