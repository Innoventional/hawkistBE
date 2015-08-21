"""empty message

Revision ID: 2e2fa9dbda8
Revises: 29e85dfb0728
Create Date: 2015-08-18 17:49:05.344260

"""

# revision identifiers, used by Alembic.
revision = '2e2fa9dbda8'
down_revision = '29e85dfb0728'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_addresses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('address_line1', sa.String(), nullable=True),
    sa.Column('address_line2', sa.String(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('postcode', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_addresses_user_id'), 'user_addresses', ['user_id'], unique=False)
    op.alter_column(u'users', 'app_wallet',
               existing_type=sa.NUMERIC(),
               nullable=False)
    op.alter_column(u'users', 'app_wallet_pending',
               existing_type=sa.NUMERIC(),
               nullable=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(u'users', 'app_wallet_pending',
               existing_type=sa.NUMERIC(),
               nullable=True)
    op.alter_column(u'users', 'app_wallet',
               existing_type=sa.NUMERIC(),
               nullable=True)
    op.drop_index(op.f('ix_user_addresses_user_id'), table_name='user_addresses')
    op.drop_table('user_addresses')
    ### end Alembic commands ###