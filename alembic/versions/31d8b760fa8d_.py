"""empty message

Revision ID: 31d8b760fa8d
Revises: 23327a8faa3
Create Date: 2015-07-01 12:55:46.504467

"""

# revision identifiers, used by Alembic.
revision = '31d8b760fa8d'
down_revision = '23327a8faa3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('items', u'selling_price')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column(u'selling_price', sa.INTEGER(), autoincrement=False, nullable=False))
    ### end Alembic commands ###