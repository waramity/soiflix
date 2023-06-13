"""empty message

Revision ID: 2c0cf1a1b417
Revises: b577eed154af
Create Date: 2021-11-27 01:11:55.909440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c0cf1a1b417'
down_revision = 'b577eed154af'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('studio',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('studio', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_studio_name'), ['name'], unique=True)

    op.create_table('tvshow_studio',
    sa.Column('studio_id', sa.Integer(), nullable=True),
    sa.Column('tvshow_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['studio_id'], ['studio.id'], ),
    sa.ForeignKeyConstraint(['tvshow_id'], ['tvshow.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tvshow_studio')
    with op.batch_alter_table('studio', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_studio_name'))

    op.drop_table('studio')
    # ### end Alembic commands ###
