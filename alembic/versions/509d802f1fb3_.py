"""empty message

Revision ID: 509d802f1fb3
Revises: 776fcafea45
Create Date: 2015-07-17 16:10:54.652041

"""

# revision identifiers, used by Alembic.
revision = '509d802f1fb3'
down_revision = '776fcafea45'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('listing_likes',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('listing_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'listing_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('listing_likes')
    ### end Alembic commands ###
