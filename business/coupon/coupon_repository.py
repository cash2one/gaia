# -*- coding: utf-8 -*-
from eaglet.core import paginator

from db.mall import promotion_models
from business import model as business_model
from business.coupon.coupon import Coupon
from business import model as business_model


class CouponRepository(business_model.Service):
	def get_coupons_for_rule(self, coupon_rule_id, filters, page_info):
		"""
		获得rule中的coupon的集合
		"""
		coupon_models = promotion_models.Coupon.select().dj_where(coupon_rule_id=coupon_rule_id)
		pageinfo, coupon_models = paginator.paginate(coupon_models, page_info.cur_page, page_info.count_per_page)

		coupons = [Coupon(coupon_model) for coupon_model in coupon_models]

		return coupons, pageinfo

	def get_coupon_by_id(self, coupon_id):
		db_model = promotion_models.Coupon.select().dj_where(id=coupon_id, owner_id=self.corp.id).first()

		coupons = Coupon.from_models({"db_models": [db_model], 'corp': self.corp})
		if coupons:
			return coupons[0]

		else:
			return None

	def get_coupon_by_ids(self, coupon_ids):
		db_models = promotion_models.Coupon.select().dj_where(id__in=coupon_ids, owner_id=self.corp.id)
		coupons = Coupon.from_models({"db_models": db_models, 'corp': self.corp})
		return coupons
