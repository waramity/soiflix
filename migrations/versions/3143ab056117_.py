"""empty message

Revision ID: 3143ab056117
Revises: 606408e171af
Create Date: 2022-07-03 23:35:00.154282

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3143ab056117'
down_revision = '606408e171af'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('post',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('thumbnail', sa.String(length=100), nullable=True),
    sa.Column('date_posted', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('post_actors',
    sa.Column('actor_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['actor_id'], ['actor.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], )
    )
    op.create_table('post_genres',
    sa.Column('genre_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post_genres')
    op.drop_table('post_actors')
    op.drop_table('post')
    # ### end Alembic commands ###
