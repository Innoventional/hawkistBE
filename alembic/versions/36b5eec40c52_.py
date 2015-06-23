"""empty message

Revision ID: 36b5eec40c52
Revises: 3fd17fd1a8cb
Create Date: 2015-06-22 17:28:50.123036

"""

# revision identifiers, used by Alembic.
revision = '36b5eec40c52'
down_revision = '3fd17fd1a8cb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password', sa.String(), nullable=True))
    op.add_column('users', sa.Column('system_status', sa.SmallInteger(), nullable=False))
    op.add_column('users', sa.Column('user_type', sa.SmallInteger(), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'user_type')
    op.drop_column('users', 'system_status')
    op.drop_column('users', 'password')
    ### end Alembic commands ###