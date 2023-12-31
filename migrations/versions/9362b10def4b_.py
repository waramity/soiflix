"""empty message

Revision ID: 9362b10def4b
Revises: c3ffb219010e
Create Date: 2021-10-26 14:05:41.335410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9362b10def4b'
down_revision = 'c3ffb219010e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('serie_list',
    sa.Column('serie_id', sa.Integer(), nullable=True),
    sa.Column('season_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['season_id'], ['season.id'], ),
    sa.ForeignKeyConstraint(['serie_id'], ['serie.id'], )
    )
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

    op.drop_table('serie_list')
    # ### end Alembic commands ###
