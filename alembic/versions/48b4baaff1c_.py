"""empty message

Revision ID: 48b4baaff1c
Revises: 136313dcff61
Create Date: 2015-07-03 22:01:27.744589

"""

# revision identifiers, used by Alembic.
revision = '48b4baaff1c'
down_revision = '136313dcff61'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('post_code', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('items', 'post_code')
    ### end Alembic commands ###
