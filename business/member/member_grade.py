# -*- coding: utf-8 -*-
"""
会员等级
"""

import json
from bs4 import BeautifulSoup
import math
from datetime import datetime

from eaglet.decorator import param_required
#from wapi import wapi_utils
from eaglet.core.cache import utils as cache_util
from db.member import models as member_models
#import resource
from eaglet.core import watchdog
from business import model as business_model
import settings
from eaglet.decorator import cached_context_property
from util import emojicons_util

DEFAULT_GRADE_NAME = u'普通会员'

class MemberGrade(business_model.Model):
    """
    会员等级
    """
    __slots__ = (
        'id',
        'name',
        'is_default_grade',
        'is_auto_upgrade',
        'pay_money',
        'pay_times'
    )

    def __init__(self, db_model):
        business_model.Model.__init__(self)
        self.context['db_model'] = db_model
        if db_model:
            self._init_slot_from_model(db_model)

    # @staticmethod
    # @param_required(['model'])
    # def from_model(args):
    #     """
    #     SocialAccount model获取SocialAccount业务对象

    #     @param[in] model: SocialAccount model

    #     @return SocialAccount业务对象
    #     """
    #     model = args['model']

    #     member_grade = MemberGrade(model)
    #     return member_grade

    @staticmethod
    def create_default_member_grade_for_corp(corp):
        if member_models.MemberGrade.select().dj_where(webapp_id=corp.webapp_id, name=DEFAULT_GRADE_NAME).count() == 0:
            return member_models.MemberGrade.create(
                webapp_id = corp.webapp_id,
                name = DEFAULT_GRADE_NAME,
                upgrade_lower_bound = 0,
                is_default_grade = True,
                is_auto_upgrade = True
            )