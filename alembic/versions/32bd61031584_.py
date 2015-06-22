"""empty message

Revision ID: 32bd61031584
Revises: af8e964cf77
Create Date: 2015-06-19 17:43:45.617494

"""

# revision identifiers, used by Alembic.
revision = '32bd61031584'
down_revision = 'af8e964cf77'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('parent_tag_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(u'ix_tags_parent_tag_id', 'tags', ['parent_tag_id'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(u'ix_tags_parent_tag_id', table_name='tags')
    op.drop_table('tags')
    ### end Alembic commands ###
