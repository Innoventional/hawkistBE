"""empty message

Revision ID: 29e85dfb0728
Revises: 3b72cfc9b5f9
Create Date: 2015-08-05 18:56:34.702179

"""

# revision identifiers, used by Alembic.
revision = '29e85dfb0728'
down_revision = '3b72cfc9b5f9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stripe_charges', sa.Column('payment_sum_without_application_fee', sa.Numeric(), nullable=True))
    op.drop_column('stripe_charges', 'application_fee_sum')
    op.add_column('users', sa.Column('app_wallet', sa.Numeric(), nullable=False))
    op.add_column('users', sa.Column('app_wallet_pending', sa.Numeric(), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'app_wallet_pending')
    op.drop_column('users', 'app_wallet')
    op.add_column('stripe_charges', sa.Column('application_fee_sum', sa.NUMERIC(), autoincrement=False, nullable=True))
    op.drop_column('stripe_charges', 'payment_sum_without_application_fee')
    ### end Alembic commands ###