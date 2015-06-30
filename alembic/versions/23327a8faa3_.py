"""empty message

Revision ID: 23327a8faa3
Revises: 36b5eec40c52
Create Date: 2015-06-30 15:25:55.734542

"""

# revision identifiers, used by Alembic.
revision = '23327a8faa3'
down_revision = '36b5eec40c52'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('category', sa.SmallInteger(), nullable=False))
    op.add_column('items', sa.Column('city', sa.String(), nullable=True))
    op.add_column('items', sa.Column('collection_only', sa.Boolean(), nullable=False))
    op.add_column('items', sa.Column('discount', sa.Integer(), nullable=True))
    op.add_column('items', sa.Column('location_lat', sa.Numeric(), nullable=True))
    op.add_column('items', sa.Column('location_lon', sa.Numeric(), nullable=True))
    op.add_column('items', sa.Column('platform', sa.SmallInteger(), nullable=False))
    op.add_column('items', sa.Column('post_code', sa.Integer(), nullable=True))
    op.add_column('items', sa.Column('retail_price', sa.Integer(), nullable=False))
    op.add_column('items', sa.Column('selling_price', sa.Integer(), nullable=False))
    op.add_column('items', sa.Column('shipping_price', sa.Integer(), nullable=True))
    op.alter_column('items', 'barcode',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('items', 'color',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('items', 'condition',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('items', 'description',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('items', 'title',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'system_status',
               existing_type=sa.SMALLINT(),
               nullable=False)
    op.alter_column('users', 'user_type',
               existing_type=sa.SMALLINT(),
               nullable=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'user_type',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.alter_column('users', 'system_status',
               existing_type=sa.SMALLINT(),
               nullable=True)
    op.alter_column('items', 'title',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('items', 'description',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('items', 'condition',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('items', 'color',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('items', 'barcode',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('items', 'shipping_price')
    op.drop_column('items', 'selling_price')
    op.drop_column('items', 'retail_price')
    op.drop_column('items', 'post_code')
    op.drop_column('items', 'platform')
    op.drop_column('items', 'location_lon')
    op.drop_column('items', 'location_lat')
    op.drop_column('items', 'discount')
    op.drop_column('items', 'collection_only')
    op.drop_column('items', 'city')
    op.drop_column('items', 'category')
    ### end Alembic commands ###
