"""empty message

Revision ID: 0c6b2b754697
Revises: 9a3f8a41c2b0
Create Date: 2021-10-26 14:02:28.180367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c6b2b754697'
down_revision = '9a3f8a41c2b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('episode_list', schema=None) as batch_op:
        batch_op.add_column(sa.Column('episode_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'episode', ['episode_id'], ['id'])
        batch_op.drop_column('serie_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('episode_list', schema=None) as batch_op:
        batch_op.add_column(sa.Column('serie_id', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'serie', ['serie_id'], ['id'])
        batch_op.drop_column('episode_id')

    # ### end Alembic commands ###
