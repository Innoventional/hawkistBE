"""empty message

Revision ID: 1a7cd6417d1e
Revises: 556a263e3d17
Create Date: 2015-07-24 18:17:49.081032

"""

# revision identifiers, used by Alembic.
revision = '1a7cd6417d1e'
down_revision = '556a263e3d17'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('listing_views',
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
    op.drop_table('listing_views')
    ### end Alembic commands ###
