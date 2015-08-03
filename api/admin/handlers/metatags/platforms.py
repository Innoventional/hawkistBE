import datetime
import logging
from sqlalchemy import func, and_
from api.admin.handlers.login import AdminBaseHandler
from api.items.models import Listing
from api.tags.models import Platform
from base import HttpRedirect
from helpers import route
from ui_messages.errors.admin_errors.tags_errors import ADMIN_TAG_EMPTY_TITLE, ADMIN_PLATFORM_ALREADY_EXISTS, \
    ADMIN_TAG_DOES_NOT_EXIST, ADMIN_TRY_DELETE_PLATFORM_WHICH_IS_USED, ADMIN_TAG_EMPTY_PLATFORM_DATA
from utility.amazon import upload_file

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('/admin/metatags/platforms')
class AdminPlatformHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        platforms = self.session.query(Platform).order_by(Platform.id)

        return self.render_string('admin/metatags/admin_platforms.html', platforms=platforms,
                                  menu_tab_active='tab_metatags')

    def create(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        platform_id = self.get_argument('editing_platform_id')
        platform_image = self.get_argument('editing_platform_image_url')
        new_platform_title = self.get_argument('new_platform_title')
        new_platform_description = self.get_argument('new_platform_description')

        if not new_platform_title or not new_platform_description or (not self.request.files and not platform_image):
            return self.make_error(ADMIN_TAG_EMPTY_PLATFORM_DATA)

        # so, if we have platform id - it is update request
        if platform_id:
            platform = self.session.query(Platform).filter(Platform.id == platform_id).first()

            if not platform:
                return self.make_error(ADMIN_TAG_DOES_NOT_EXIST % ('platform', platform_id))

            print platform

            already_exists = self.session.query(Platform).filter(and_(func.lower(Platform.title) == new_platform_title.lower(),
                                                                      Platform.id != platform.id)).first()

            if already_exists:
                return self.make_error(ADMIN_PLATFORM_ALREADY_EXISTS % new_platform_title.upper())

            need_commit = False
            if platform.title != new_platform_title:
                platform.title = new_platform_title
                need_commit = True

            if platform.description != new_platform_description:
                platform.description = new_platform_description
                need_commit = True

            if self.request.files:
                img = self.request.files.values()[0][0]['body']
                image_url = upload_file('platform-%s' % platform.id, img, content_type='image/jpeg')
                platform.image_url = image_url
                need_commit = True

            if need_commit:
                platform.updated_at = datetime.datetime.utcnow()
                self.session.commit()
            return self.success()

        already_exists = self.session.query(Platform).filter(func.lower(Platform.title) == new_platform_title.lower()).first()

        if already_exists:
            return self.make_error(ADMIN_PLATFORM_ALREADY_EXISTS % new_platform_title.upper())

        new_platform = Platform()
        new_platform.created_at = datetime.datetime.utcnow()
        new_platform.updated_at = datetime.datetime.utcnow()
        new_platform.title = new_platform_title
        new_platform.description = new_platform_description
        self.session.add(new_platform)

        # add platform image
        img = self.request.files.values()[0][0]['body']
        image_url = upload_file('platform-%s' % new_platform.id, img, content_type='image/jpeg')
        new_platform.image_url = image_url

        self.session.commit()
        return self.success()

    def update(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        platform_id = self.get_argument('platform_id')
        platform_title = self.get_argument('platform_title')

        if not platform_id:
            return self.make_error("Empty platform id. Backend failure")

        if not platform_title:
            return self.make_error(ADMIN_TAG_EMPTY_TITLE % 'platform')

        platform = self.session.query(Platform).filter(Platform.id == platform_id).first()
        if not platform:
            return self.make_error(ADMIN_TAG_DOES_NOT_EXIST % ('platform', platform_id))

        already_exists = self.session.query(Platform).filter(and_(func.lower(Platform.title) == platform_title.lower(),
                                                                  Platform.id != platform.id)).first()

        if already_exists:
            return self.make_error(ADMIN_PLATFORM_ALREADY_EXISTS % platform_title.upper())

        # check is title change
        if platform.title != platform_title:
            platform.title = platform_title
            platform.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        return self.success()

    def remove(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        platform_id = self.get_arg('platform_id')
        platform = self.session.query(Platform).filter(Platform.id == platform_id).first()

        if not platform:
            return self.make_error(ADMIN_TAG_DOES_NOT_EXIST % ('platform', platform_id))

        # check is this platform using
        used = self.session.query(Listing).filter(Listing.platform == platform).first()
        if used:
            return self.make_error(ADMIN_TRY_DELETE_PLATFORM_WHICH_IS_USED % platform.title.upper())

        self.session.delete(platform)
        self.session.commit()
        return self.success()