"""empty message

Revision ID: 3c4f44d84b19
Revises: 509d802f1fb3
Create Date: 2015-07-20 14:50:01.315992

"""

# revision identifiers, used by Alembic.
revision = '3c4f44d84b19'
down_revision = '509d802f1fb3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('user_to_see_id', sa.Integer(), nullable=True))
    op.create_index(u'ix_comments_user_to_see_id', 'comments', ['user_to_see_id'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(u'ix_comments_user_to_see_id', table_name='comments')
    op.drop_column('comments', 'user_to_see_id')
    ### end Alembic commands ###