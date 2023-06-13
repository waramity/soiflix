"""empty message

Revision ID: 09fa7aadf69c
Revises: 70f441440803
Create Date: 2021-10-11 12:04:58.645714

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09fa7aadf69c'
down_revision = '70f441440803'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('series', schema=None) as batch_op:
        batch_op.add_column(sa.Column('yt_playlist_url', sa.String(length=100), nullable=False))
        batch_op.drop_column('image')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('series', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.VARCHAR(length=100), nullable=False))
        batch_op.drop_column('yt_playlist_url')

    # ### end Alembic commands ###
