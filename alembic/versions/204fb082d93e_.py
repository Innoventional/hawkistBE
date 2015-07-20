"""empty message

Revision ID: 204fb082d93e
Revises: 3c4f44d84b19
Create Date: 2015-07-20 16:05:32.314628

"""

# revision identifiers, used by Alembic.
revision = '204fb082d93e'
down_revision = '3c4f44d84b19'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_reportlist',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('reported_user_id', sa.Integer(), nullable=False),
    sa.Column('reason', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['reported_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'reported_user_id')
    )
    op.create_table('user_blacklist',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('blocked_user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['blocked_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'blocked_user_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_blacklist')
    op.drop_table('user_reportlist')
    ### end Alembic commands ###
