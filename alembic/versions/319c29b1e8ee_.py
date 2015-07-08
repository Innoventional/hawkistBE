"""empty message

Revision ID: 319c29b1e8ee
Revises: 48b4baaff1c
Create Date: 2015-07-08 10:54:25.284580

"""

# revision identifiers, used by Alembic.
revision = '319c29b1e8ee'
down_revision = '48b4baaff1c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('platforms',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('platform_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['platform_id'], ['platforms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(u'ix_categories_platform_id', 'categories', ['platform_id'], unique=False)
    op.create_table('subcategories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(u'ix_subcategories_category_id', 'subcategories', ['category_id'], unique=False)
    op.create_table('conditions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('subcategory_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['subcategory_id'], ['subcategories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(u'ix_conditions_subcategory_id', 'conditions', ['subcategory_id'], unique=False)
    op.create_table('colors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('code', sa.String(), nullable=True),
    sa.Column('subcategory_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['subcategory_id'], ['subcategories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(u'ix_colors_subcategory_id', 'colors', ['subcategory_id'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(u'ix_colors_subcategory_id', table_name='colors')
    op.drop_table('colors')
    op.drop_index(u'ix_conditions_subcategory_id', table_name='conditions')
    op.drop_table('conditions')
    op.drop_index(u'ix_subcategories_category_id', table_name='subcategories')
    op.drop_table('subcategories')
    op.drop_index(u'ix_categories_platform_id', table_name='categories')
    op.drop_table('categories')
    op.drop_table('platforms')
    ### end Alembic commands ###
