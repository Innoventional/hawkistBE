import datetime
from sqlalchemy import Column, Integer, DateTime, String, Numeric, SmallInteger, Enum
from orm import Base

__author__ = 'ne_luboff'


class WithdrawalStatus(Enum):
    New = 0
    InProcess = 1
    Completed = 2


class UserWithdrawal(Base):
    __tablename__ = 'user_withdrawal'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    stripe_transfer_id = Column(String, nullable=False)

    # info about user who want withdrawal
    user_id = Column(Integer, nullable=False)
    user_username = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    account_holder = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    account_sort_code = Column(String, nullable=False)

    amount_total = Column(Numeric, nullable=False)
    amount = Column(Numeric, nullable=False)

    status = Column(SmallInteger, nullable=False, default=WithdrawalStatus.New)
