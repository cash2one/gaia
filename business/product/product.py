# -*- coding: utf-8 -*-
from datetime import datetime
import json
from bdem import msgutil

import settings
from eaglet.decorator import param_required
from eaglet.utils.resource_client import Resource

from db.mall import models as mall_models
from db.mall import promotion_models
from db.account import models as account_models
from business.account.user_profile import UserProfile
from business import model as business_model
from eaglet.core import watchdog
from eaglet.core.exceptionutil import unicode_full_stack
from settings import PANDA_IMAGE_DOMAIN


from business.decorator import cached_context_property


class Product(business_model.Model):
	"""
	商品
	"""
	__slots__ = (
		'id',
		'owner_id',
		'type',
		'create_type',
		'is_deleted',
		'name',
		'display_index',
		'is_member_product',
		'weshop_sync',
		'shelve_type',
		'shelve_start_time',
		'shelve_end_time',
		'detail',
		'thumbnails_url',
		'order_thumbnails_url',
		'pic_url',
		'swipe_images',
		'detail_link',
		'bar_code',
		'min_limit',
		'categories',
		'id2category',
		'properties',
		'created_at',

		#供应商信息
		'supplier_id',
		'supplier',
		'classification_lists',
		#'supplier_user_id',

		#商品规格信息
		'is_use_custom_model',
		#'model_name',
		#'product_model_properties',
		'standard_model',
		'custom_models',
		'used_system_model_properties',

		#物流信息
		'postage_id',
		'postage_type',
		'unified_postage_money',

		#价格、销售信息
		'price_info',
		'sales',
		'is_sellout',
		'is_use_online_pay_interface',
		'is_use_cod_pay_interface',
		'product_promotion_title', #商品的促销标题
		'is_enable_bill',
		'buy_in_supplier',

		#促销信息
		'promotion',
		'promotion_title', #商品关联的促销活动的促销标题
		'integral_sale',
		'product_review',
		'is_deleted',
		'is_delivery', # 是否勾选配送时间
		# 'supplier_name' # 供货商名称
		'purchase_price',
		'price',
		'weight',
		'stock_type',
		'limit_zone_type',
		'limit_zone'
	)

	def __init__(self, model=None):
		business_model.Model.__init__(self)
		self.promotion = None

		if model:
			self._init_slot_from_model(model)
			self.owner_id = model.owner_id
			self.min_limit = model.stocks
			self.thumbnails_url = '%s%s' % (settings.IMAGE_HOST, model.thumbnails_url) if model.thumbnails_url.find('http') == -1 else model.thumbnails_url
			self.pic_url = '%s%s' % (settings.IMAGE_HOST, model.pic_url) if model.pic_url.find('http') == -1 else model.pic_url
			self.custom_models = []
			self.swipe_images = []
			self.categories = []
			self.properties = []
			self.classification_lists = []
			self.sales = 0
			self.supplier_id = self.supplier
			self.supplier = None

	@property
	def is_sellout(self):
		"""
		[property] 是否卖光
		"""
		return self.total_stocks <= 0

	@is_sellout.setter
	def is_sellout(self, value):
		"""
		[property setter] 是否卖光
		"""
		pass

	@property
	def total_stocks(self):
		"""
		[property] 商品总库存
		"""
		context = self.context
		if not 'total_stocks' in context:
			context['total_stocks'] = 0
			models = self.models
			# if self.is_use_custom_model:
			# 	models = self.models[1:]
			# else:
			# 	models = self.models

			if not models or len(models) == 0:
				context['total_stocks'] = 0
				return context['total_stocks']
			is_dict = (type(models[0]) == dict)

			# for model in models:
			# 	stock_type = model['stock_type'] if is_dict else model.stock_type
			# 	stocks = model['stocks'] if is_dict else model.stocks
			# 	if stock_type == mall_models.PRODUCT_STOCK_TYPE_UNLIMIT:
			# 		context['total_stocks'] = u'无限'
			# 		return context['total_stocks']
			# 	else:
			# 		context['total_stocks'] = context['total_stocks'] + stocks

			# 有无限的规格
			has_unlimited_model = False
			for model in models:
				stock_type = model['stock_type'] if is_dict else model.stock_type
				if stock_type == mall_models.PRODUCT_STOCK_TYPE_UNLIMIT:
					has_unlimited_model = True
					break
			if has_unlimited_model:
				context['total_stocks'] = u'无限'
				return context['total_stocks']
			else:
				realtime_stock = RealtimeStock.from_product_id({
					'product_id': self.id
				}).model2stock
				stock_dicts = realtime_stock.values()
				# stock_dicts:[{'stock_type': 1, 'stocks': 1}, {'stock_type': 1, 'stocks': 2}, {'stock_type': 1, 'stocks': 3}]
				for s in stock_dicts:
					context['total_stocks'] = context['total_stocks'] + s['stocks']

		return context['total_stocks']

	# 如果规格有图片就显示，如果没有，使用缩略图
	@property
	def order_thumbnails_url(self):
		"""
		[property] 订单中的缩略图
		"""
		'''
		if hasattr(self, 'custom_model_properties') and self.custom_model_properties:
			for model in self.custom_model_properties:
				if model['property_pic_url']:
					return model['property_pic_url']
		'''
		context = self.context
		if not 'order_thumbnails_url' in context:
			context['order_thumbnails_url'] = self.thumbnails_url
		return context['order_thumbnails_url']

	@order_thumbnails_url.setter
	def order_thumbnails_url(self, url):
		"""
		[property setter] 订单中的缩略图
		"""
		# self.context['order_thumbnails_url'] = url
		self.thumbnails_url = url

	@property
	def hint(self):
		"""
		[property] 判断商品是否被禁止使用全场优惠券
		"""
		corp = self.context['corp']
		forbidden_coupon_product_ids = ForbiddenCouponProductIds.get_for_corp({
			'corp': corp
		}).ids
		if self.id in forbidden_coupon_product_ids:
			return u'该商品不参与全场优惠券使用！'
		else:
			return u''

	def is_on_shelve(self):
		"""
		判断商品是否是上架状态
		"""
		return self.shelve_type == 'on_shelf'

	def set_shelve_type(self, shelve_type):
		"""
		设置商品的货架状态
		"""
		self.shelve_type = shelve_type

	def apply_discount(self, webapp_user):
		"""
		执行webapp_user携带的折扣信息

		Parameters
			[in] webapp_user
		"""
		if self.is_member_product:
			_, discount_value = webapp_user.member.discount
			discount = discount_value / 100.0

			self.price_info['min_price'] = round(self.price_info['min_price'] * discount, 2) #折扣后的价格
			self.price_info['max_price'] = round(self.price_info['max_price'] * discount, 2) #折扣后的价格
			self.price_info['display_price'] = round(float(self.price_info['display_price']) * discount, 2) #折扣后的价格

			for model in self.models:
				model.price = round(model.price * discount, 2)

	@cached_context_property
	def __deleted_models(self):
		return list(mall_models.ProductModel.select().dj_where(product_id=self.id, is_deleted=True))

	def get_specific_model(self, model_name):
		"""
		获得特定的商品规格信息

		@param [in] model_name: 商品规格名

		@return ProductModel对象

		注意，这里返回的有可能是被删除的规格，使用者应该通过product_model.is_deleted来判断
		"""
		models = self.models
		if not models:
			watchdog.info({
				'msg': u'商品models为空！',
				'product_id': self.id,
				'product_detail': self.to_dict()
			})
			Product.__fill_model_detail(self.context['corp'], [self], True)
			models = self.models
		candidate_models = filter(lambda m: m.name == model_name if m else False, models)
		if len(candidate_models) > 0:
			model = candidate_models[0]
			return model
		else:
			candidate_models = filter(lambda m: m.name == model_name if m else False, self.__deleted_models)
			if len(candidate_models) > 0:
				model = candidate_models[0]
				return model
			else:
				return None

	# def after_from_dict(self):
	# 	product_models = []
	# 	for model_dict in self.models:
	# 		product_models.append(ProductModel.from_dict(model_dict))
	# 	self.models = product_models

	# 	if self.promotion:
	# 		self.promotion = PromotionRepository.get_promotion_from_dict_data(self.promotion)

	# 		if not self.promotion.is_active():
	# 			#缓存中的促销已过期
	# 			self.promotion = None

	# 	if self.integral_sale:
	# 		self.integral_sale = PromotionRepository.get_promotion_from_dict_data(self.integral_sale)

	# 		if not self.integral_sale.is_active():
	# 			self.integral_sale = None

	@cached_context_property
	def supplier_name(self):
		try:
			# 非微众系列商家
			if not self.context['corp'].user_profile.webapp_type:
				return ''
			# 手动添加的供货商
			if self.supplier:
				return Supplier.get_supplier_name(self.supplier)
			# 同步的供货商
			relation = mall_models.WeizoomHasMallProductRelation.select().dj_where(weizoom_product_id=self.id).first()
			if relation:
				supplier_name = account_model.UserProfile.select().dj_where(user_id=relation.mall_id).first().store_name
			else:
				supplier_name = ''

			return supplier_name
		except:
			watchdog.alert(unicode_full_stack())
			return ''

	@cached_context_property
	def supplier_postage_config(self):
		if not self.supplier:
			return {}

		supplier_postage_config_model = mall_models.SupplierPostageConfig.select().dj_where(
				supplier_id=self.supplier,
				status=True
			).first()
		if supplier_postage_config_model and supplier_postage_config_model.postage:
			return {
				'condition_type': supplier_postage_config_model.condition_type,
				'condition_money': supplier_postage_config_model.condition_money,
				'postage': supplier_postage_config_model.postage
			}
		else:
			return {}

	@cached_context_property
	def use_supplier_postage(self):
		if not self.supplier:
			return False
		supplier_model = mall_models.Supplier.select().dj_where(id=self.supplier).first()
		user_profile = account_model.UserProfile.select().dj_where(user_id=supplier_model.owner_id).first()
		if supplier_model.name == u'自营' and user_profile.webapp_type == 3:
			return False
		else:
			return True

	def update_sales(self,count):
		"""
		更新商品销量
		@param count: 正数表示增加销量，负数表示减少销量
		@return:
		"""
		if mall_models.ProductSales.select().dj_where(product_id=self.id).first():
			mall_models.ProductSales.update(
				sales=mall_models.ProductSales.sales + count).dj_where(product_id=self.id).execute()
		else:
			mall_models.ProductSales.create(product=self.id, sales=self.count)

	def is_supplied_by_supplier(self):
		"""
		判断商品是否由供应商提供
		"""
		return self.supplier != 0

	# def _post_action(self):
	# 	"""
	# 	内部方法，将mall_model.Product中与Product领域对象同名的属性做调整，使之符合业务领域
	# 	仅在product内部调用，外部不要使用此方法
	# 	"""
	# 	if self.supplier == 0:
	# 		self.supplier = None