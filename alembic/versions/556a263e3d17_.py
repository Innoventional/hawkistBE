"""empty message

Revision ID: 556a263e3d17
Revises: 4be90e7c3be1
Create Date: 2015-07-23 16:26:08.878856

"""

# revision identifiers, used by Alembic.
revision = '556a263e3d17'
down_revision = '4be90e7c3be1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comment_mentioned_users',
    sa.Column('comment_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('comment_id', 'user_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comment_mentioned_users')
    ### end Alembic commands ###
