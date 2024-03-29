"""empty message

Revision ID: dee0f512696
Revises: 4e1127937153
Create Date: 2015-07-15 14:53:47.388542

"""

# revision identifiers, used by Alembic.
revision = 'dee0f512696'
down_revision = '4e1127937153'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('listings', 'sold',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.add_column('users', sa.Column('city', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_activity', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_activity')
    op.drop_column('users', 'city')
    op.alter_column('listings', 'sold',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    ### end Alembic commands ###
