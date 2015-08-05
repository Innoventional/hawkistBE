import datetime
from sqlalchemy import and_
from api.items.models import Listing, ListingStatus
from api.payments.models import StripeCharges, ChargesStatus

__author__ = 'ne_luboff'


def check_pending_payments(self):
    """
    Then someone (buyer) press 'Buy' on payment screes item purchase process started.
    Listing to buy status changed to reserved.
    Created charges. Initial charge status - Active.
    Buyer has 7 days to press receive item button (send money to seller app) or mark order Has an Issue flag.
    If order marked as a Has an issue changed charge status changed to Frozen and start buyer communication
    with support agents.
    If order marked as Received charge status change to Finished and money send to seller Hawkist wallet.
    After 7 days money will send to seller wallet automatically.
    """
    # first get all user not active listings id
    reserved_user_listing_ids = [l.id for l in self.session.query(Listing).filter(and_(Listing.user_id == self.user.id,
                                                                                       Listing.status == ListingStatus.Reserved))]
    # after it select all charges that are active and must be finished
    pending_charges = self.session.query(StripeCharges).filter(and_(StripeCharges.listing_id.in_(reserved_user_listing_ids),
                                                                    StripeCharges.system_status == ChargesStatus.Active,
                                                                    # StripeCharges.date_finish > datetime.datetime.utcnow()))
                                                                    StripeCharges.date_finish < datetime.datetime.utcnow()))

    # go through every pending charge and send money to app wallet
    for pending_charge in pending_charges:
        # send money to wallet
        pending_charge.listing.user.app_wallet_pending -= pending_charge.charge.payment_sum_without_application_fee
        pending_charge.listing.user.app_wallet += pending_charge.charge.payment_sum_without_application_fee
        # if pending_charge.listing.user.app_wallet:
        #     pending_charge.listing.user.app_wallet += pending_charge.payment_sum_without_application_fee
        # else:
        #     pending_charge.listing.user.app_wallet = 0
        #     pending_charge.listing.user.app_wallet += pending_charge.payment_sum_without_application_fee
        # change charge status
        pending_charge.system_status = ChargesStatus.Finished
