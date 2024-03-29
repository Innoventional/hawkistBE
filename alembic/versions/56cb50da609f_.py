"""empty message

Revision ID: 56cb50da609f
Revises: 3df51bdb7844
Create Date: 2015-06-09 16:51:24.120984

"""

# revision identifiers, used by Alembic.
revision = '56cb50da609f'
down_revision = '3df51bdb7844'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email_salt', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_pin_sending', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('sent_pins_count', sa.SmallInteger(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'sent_pins_count')
    op.drop_column('users', 'last_pin_sending')
    op.drop_column('users', 'email_salt')
    ### end Alembic commands ###
