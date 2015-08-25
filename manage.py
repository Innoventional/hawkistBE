import logging
from optparse import OptionParser, OptionGroup
import sys
from migrate.versioning import api as migrate_api
from tornado import httpserver, ioloop
from app import HawkistApi
from environment import env
from orm import create_session
from utility.cron_scripts import timer_event

LOG_FORMAT = '[%(asctime)s] %(levelname)s [line:%(lineno)s] [%(funcName)s] %(message)s'
logging.basicConfig(format=LOG_FORMAT)

logger = logging.getLogger(__name__)


class ApiManager(object):
    def __init__(self, argv):
        parser = OptionParser(
            usage="manage.py [options] mode",
            description='ORLY!'
        )
        mode_group = OptionGroup(parser, "Mode options (only specify one)")
        parser.add_option_group(mode_group)

        parser.add_option('-d', '--debug', action='store_true', help='Display debug output')
        parser.add_option('-f', '--force', action='store_true', help='Force action')

        (self.options, self.args) = parser.parse_args(argv)
        if len(self.args) == 1:
            print >>sys.stderr, parser.description + '\n'
            print >>sys.stderr, 'Usage:', parser.usage
            print >>sys.stderr, "Modes:"
            for i in filter(lambda i: i.startswith('do_'), dir(self)):
                f = getattr(self, i)
                print >>sys.stderr, "\t%s: %s" % (i[3:], f.__doc__)
            sys.exit()

        self.debug = self.options.debug or env['debug']
        self.force = self.options.force

        env['debug'] = self.debug

        if self.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)

        getattr(self, 'do_' + self.args[1])(*self.args[2:])

    def do_run(self):
        '''Runs server'''
        logger.debug('Starting Hawkist API server...')

        daemon_mode = env.get('daemon', False)
        if daemon_mode is True:
            logfile = open(env['logfile'], 'a+')

            from daemon import pidfile, DaemonContext
            pid = pidfile.TimeoutPIDLockFile(env['pidfile'], 10)
            logger.debug('Pidfile: %s', env['pidfile'])
            ctx = DaemonContext(stdout=logfile, stderr=logfile, working_directory='.', pidfile=pid)
            ctx.open()

        interface, port = env['listen'].split(':')

        http_server = httpserver.HTTPServer(HawkistApi())
        http_server.listen(int(port), interface)
        logger.debug("Bind to %s:%s", interface, port)
        ioloop.IOLoop.instance().start()

    def do_db_init(self):
        '''Initializes empty database'''
        logger.debug('Initializing Hawkist API database %s...', env['db'])
        migrate_api.version_control(env['db'], 'migrations')

    def do_db_version(self):
        '''Prints version of the database'''
        print 'Database version:', migrate_api.db_version(env['db'], 'migrations')

    def do_new_migration(self, description):
        '''Creates new migration script'''
        migrate_api.script(description, 'migrations', templates_path='migrations', templates_theme='default')

    def do_db_upgrade(self):
        '''Tests migrations'''
        migrate_api.upgrade(env['db'], 'migrations')

    def do_db_downgrade(self, version):
        '''DB downgrade'''
        migrate_api.downgrade(env['db'], 'migrations', version)

    def do_create_api_key(self):
        from uuid import uuid4
        from api.models import ApiKey

        session = create_session()

        old_keys = session.query(ApiKey)

        for old_key in old_keys:
            session.delete(old_key)

        u = str(uuid4()).replace('-', '')
        api_key, api_pass = u[:16], u[16:]
        key = ApiKey(api_key=api_key, api_pass=api_pass)
        session.add(key)
        session.commit()
        session.remove

        print 'API Key: ', api_key
        print 'API Pass:', api_pass

    def do_timer_event(self):
        import datetime
        from api.items.models import Listing, ListingStatus
        from api.orders.models import UserOrders, OrderStatus
        from api.users.models import User, SystemStatus
        from utility.average_response_time import calculate_average_response_time
        from utility.notifications import notification_item_received, notification_funds_released
        from utility.send_email import send_warning_4_6_days_email, funds_received_seller

        session = create_session()
        """
        First send all messages.
        Function for sending 4 days notification to email and user notification screen if order is active
        """
        logger.debug('Start cron script')
        logger.debug('%s' % datetime.datetime.utcnow())
        orders = session.query(UserOrders).filter(UserOrders.order_status == OrderStatus.Active)
        for order in orders:
            # check time difference
            time_delta = datetime.datetime.utcnow() - order.created_at
            if 7 > time_delta.days >= 4:
                # send 4 days warning letter
                send_warning_4_6_days_email(order.user.email, order.user.username, order.listing.title)
                # add notifications
                notification_item_received(session, order.user_id, order.listing)
            elif time_delta.days >= 7:
                # first we must transfer money from pending balance to available
                order.listing.user.app_wallet_pending -= order.payment_sum_without_application_fee
                order.listing.user.app_wallet += order.payment_sum_without_application_fee
                order.order_status = OrderStatus.FundsReleasedByTimer
                session.commit()
                # send email notification to seller
                funds_received_seller(order)
                # add notification
                notification_funds_released(session, order.user, order.listing)
        """
        Then check all reserved listings
        """
        listings = session.query(Listing).filter(Listing.reserved_by_user == True)
        for listing in listings:
            time_delta = datetime.datetime.utcnow() - listing.reserve_time
            if time_delta.days >= 1:
                # make this listing available
                listing.selling_price = listing.previous_price
                listing.reserved_by_user = False
                listing.status = ListingStatus.Active
        """
        Recalculate response time for every user
        """
        users = session.query(User).filter(User.system_status == SystemStatus.Active)
        for user in users:
            user.average_response_time = calculate_average_response_time(user)
        session.commit()


if __name__ == '__main__':
    ApiManager(sys.argv)
