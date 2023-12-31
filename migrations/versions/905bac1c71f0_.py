"""empty message

Revision ID: 905bac1c71f0
Revises: b268bfb7db5a
Create Date: 2021-10-25 23:09:28.489093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '905bac1c71f0'
down_revision = 'b268bfb7db5a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('episode')
    op.drop_table('series_genres')
    op.drop_table('episode_list')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('episode_list',
    sa.Column('episode_id', sa.INTEGER(), nullable=True),
    sa.Column('season_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['episode_id'], ['episode.id'], ),
    sa.ForeignKeyConstraint(['season_id'], ['season.id'], )
    )
    op.create_table('series_genres',
    sa.Column('genre_id', sa.INTEGER(), nullable=True),
    sa.Column('series_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
    sa.ForeignKeyConstraint(['series_id'], ['series.id'], )
    )
    op.create_table('episode',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=100), nullable=False),
    sa.Column('youtube_url', sa.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
