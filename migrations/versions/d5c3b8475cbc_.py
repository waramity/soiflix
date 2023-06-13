"""empty message

Revision ID: d5c3b8475cbc
Revises: ec215c0b0850
Create Date: 2021-10-26 14:08:08.763219

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5c3b8475cbc'
down_revision = 'ec215c0b0850'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('series_list',
    sa.Column('serie_id', sa.Integer(), nullable=True),
    sa.Column('season_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['season_id'], ['season.id'], ),
    sa.ForeignKeyConstraint(['serie_id'], ['serie.id'], )
    )
    op.drop_table('episode_list')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('episode_list',
    sa.Column('serie_id', sa.INTEGER(), nullable=True),
    sa.Column('season_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['season_id'], ['season.id'], ),
    sa.ForeignKeyConstraint(['serie_id'], ['serie.id'], )
    )
    op.drop_table('series_list')
    # ### end Alembic commands ###
