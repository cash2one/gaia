# -*- coding: utf-8 -*-
"""@package business.mall.order_products
订单商品(OrderPdocut)集合

OrderProducts用于构建一组OrderProduct，OrderProducts存在的目的是为了后续优化，以最少的数据库访问次数对商品信息进行批量填充

"""

import json

from eaglet.decorator import param_required

import settings
from business.order.delivery_item_product import DeliveryItemProduct
from db.mall import models as mall_models
from business import model as business_model


class DeliveryItemProductRepository(business_model.Model):
	# __slots__ = (
	# 	'corp'
	# )

	def __init__(self, corp):

		business_model.Model.__init__(self)

		self.corp = corp

	@staticmethod
	@param_required(['corp'])
	def get(args):
		corp = args['corp']

		return DeliveryItemProductRepository(corp)

	def set_products_for_delivery_items(self, delivery_items):
		"""
		设置订单的商品，性能攸关
		@param delivery_items:
		@return:
		"""

		# todo 需要重新mall_order_has_product表，需要记录product_name,thumbnail_url,weight,product_model_name_texts

		origin_order_ids = []
		delivery_item_ids = []
		delivery_item_id2origin_order_id = {}
		for delivery_item in delivery_items:
			delivery_item_ids.append(delivery_item.id)
			origin_order_ids.append(delivery_item.origin_order_id)
			delivery_item_id2origin_order_id[delivery_item.id] = delivery_item.origin_order_id
		ohs_db_model_list = mall_models.OrderHasProduct.select().dj_where(order_id__in=delivery_item_ids)

		# promotion_id2order_has_promotion = {str(r.promotion_id) + str(r.order_id): r for r in
		#                 mall_models.OrderHasPromotion.select().dj_where(order_id__in=origin_order_ids)}

		# 为了兼容积分应用的promotion都是0
		promotion_id2order_has_promotion = {}
		for r in mall_models.OrderHasPromotion.select().dj_where(order_id__in=origin_order_ids):
			flag = str(r.promotion_id) + str(r.order_id)
			if flag in promotion_id2order_has_promotion:
				promotion_id2order_has_promotion[flag].append(r)
			else:
				promotion_id2order_has_promotion[flag] = [r]

		# [compatibility]: 兼容apiserver产生的出货单的order_has_prduct时候，total_price和price写入的采购价
		origin_ohs_list = mall_models.OrderHasProduct.select().dj_where(order_id__in=origin_order_ids)

		# premium_product_ids = []
		# for promotion in id2promotion.values():
		# 	if promotion.promotion_type == 'premium_sale':
		# 		db_promotion_result = json.loads(promotion.promotion_result_json)
		# 		premium_product_ids.extend(p['id'] for p in db_promotion_result['premium_products'])

		# current_premium_products = self.corp.product_pool.get_products_by_ids(premium_product_ids,
		#                                                                       {"with_product_model": True,
		#                                                                        "with_property": True,
		#                                                                        "with_model_property_info": True})
		# id2current_premium_products = {p.id: p for p in current_premium_products}

		delivery_item_ohs_id2origin_order_ohs = {}

		product_ids = []
		custom_model_names = []
		for delivery_item_ohs in ohs_db_model_list:
			if delivery_item_ohs.product_model_name != 'standard':
				custom_model_names.append(delivery_item_ohs.product_model_name)
			for origin_ohs in origin_ohs_list:
				# if delivery_item_ohs.origin_order_id == origin_ohs.order_id and delivery_item_ohs.product_id == origin_ohs.product_id:
				if delivery_item_id2origin_order_id[
					delivery_item_ohs.order_id] == origin_ohs.order_id and delivery_item_ohs.product_id == origin_ohs.product_id and delivery_item_ohs.product_model_name == origin_ohs.product_model_name:
					delivery_item_ohs_id2origin_order_ohs[delivery_item_ohs.id] = origin_ohs
					break

			product_ids.append(delivery_item_ohs.product_id)

		# products = self.corp.product_pool.get_products_by_ids(product_ids,
		#                                                       {"with_product_model": True, "with_property": True,
		#                                                        "with_model_property_info": True})
		# product_id2product = {p.id: p for p in products}

		delivery_item_products = []
		for r in ohs_db_model_list:

			promotion_info = {
				'type': '',
				'integral_money': 0,
				'integral_count': 0,
				'grade_discount_money': 0,
				'promotion_saved_money': 0
			}

			# product = product_id2product[r.product_id]

			# promotion = id2promotion.get(r.promotion_id, None)
			#
			# if promotion:
			# 	db_promotion_result = json.loads(promotion.promotion_result_json)
			# 	# type种类:flash_sale、integral_sale、premium_sale
			# 	promotion_info['type'] = promotion.promotion_type

			delivery_item_product = DeliveryItemProduct()
			delivery_item_product.name = r.product_name
			delivery_item_product.id = r.product_id
			# delivery_item_product.origin_price = r.total_price / r.number
			# delivery_item_product.sale_price = r.price

			# [compatibility]: 兼容apiserver产生的出货单的order_has_prduct时候，total_price和price写入的采购价
			origin_ohs = delivery_item_ohs_id2origin_order_ohs.get(r.id, r)

			delivery_item_product.origin_price = origin_ohs.total_price / r.number
			delivery_item_product.sale_price = origin_ohs.price
			delivery_item_product.total_origin_price = origin_ohs.total_price
			delivery_item_product.count = r.number
			delivery_item_product.product_model_name = r.product_model_name
			delivery_item_product.delivery_item_id = r.order_id
			delivery_item_product.context['index'] = r.id

			delivery_item_product.model_id = r.product_model_id
			delivery_item_product.product_model_name_texts = json.loads(r.product_model_name_texts)
			delivery_item_product.weight = r.weight

			delivery_item_product.thumbnails_url = r.thumbnail_url
			delivery_item_product.user_code = r.product.user_code

			promotions = promotion_id2order_has_promotion.get(str(r.promotion_id) + str(r.origin_order_id), [])

			if promotions:
				promotion = promotions[0]
				db_promotion_result = json.loads(promotion.promotion_result_json)

				if promotion and promotion.promotion_type == 'premium_sale':
					# 将premium_product转换为order product
					db_promotion_result_version = db_promotion_result.get('version', '0')
					# 兼容weapp少量遗留订单产生错误数据，使得手机端和后台显示一致
					if not db_promotion_result.get('premium_products'):
						continue
					for premium_product in db_promotion_result['premium_products']:
						premium_delivery_item_product = DeliveryItemProduct()
						premium_delivery_item_product.name = premium_product['name']
						if db_promotion_result_version == settings.PROMOTION_RESULT_VERSION:
							premium_delivery_item_product.count = premium_product['premium_count']
							premium_delivery_item_product.thumbnails_url = '%s%s' % (
								settings.IMAGE_HOST, premium_product['thumbnails_url']) if premium_product[
									                                                           'thumbnails_url'].find(
								'http') == -1 else premium_product['thumbnails_url']
						else:
							premium_delivery_item_product.count = premium_product['count']
							premium_delivery_item_product.thumbnails_url = '%s%s' % (
								settings.IMAGE_HOST, premium_product['thumbnails_url']) if premium_product[
									                                                           'thumbnails_url'].find(
								'http') == -1 else premium_product['thumbnails_url']
						premium_delivery_item_product.id = premium_product['id']

						# current_premium_product = id2current_premium_products[premium_product['id']]

						premium_delivery_item_product.weight = premium_product.get('weight', 0)

						premium_delivery_item_product.promotion_info = {
							'type': 'premium_sale:premium_product',  # 赠品
							'integral_money': 0,
							'integral_count': 0,
							'grade_discount_money': 0,
							'promotion_saved_money': 0
						}

						premium_delivery_item_product.delivery_item_id = r.order_id
						premium_delivery_item_product.context['index'] = r.id + 1
						premium_delivery_item_product.origin_price = premium_product.get('price', 0)
						premium_delivery_item_product.sale_price = 0
						premium_delivery_item_product.total_origin_price = 0
						premium_delivery_item_product.product_model_name_texts = []

						delivery_item_products.append(premium_delivery_item_product)

				# 填充会员等级价金额
				if r.grade_discounted_money:
					promotion_info['grade_discount_money'] = r.grade_discounted_money

				# 填充限时抢购金额
				if promotion.promotion_type == "flash_sale":
					promotion_info['promotion_saved_money'] = round(db_promotion_result['promotion_saved_money'], 2)
					promotion_info['type'] = "flash_sale"

				for promotion in promotions:
					# 填充积分应用
					db_promotion_result = json.loads(promotion.promotion_result_json)

					integral_product_info = db_promotion_result.get('integral_product_info')
					if integral_product_info:

						if integral_product_info == str(
								delivery_item_product.id) + '-' + delivery_item_product.product_model_name:
							promotion_info['integral_money'] = round(promotion.integral_money, 2)
							promotion_info['integral_count'] = promotion.integral_count

							if not promotion_info['type']:
								promotion_info['type'] = 'integral_sale'

			delivery_item_product.promotion_info = promotion_info

			# delivery_item_product_info = {
			# 	'rid': r.id,
			# 	'id': r.product_id,
			# 	'model_name': r.product_model_name,
			# 	'count': r.number,
			# 	'promotion_id': r.promotion_id,
			# 	'price': r.price,
			# 	'total_price': r.total_price,
			# 	'promotion_money': r.promotion_money,
			# 	'discount_money': r.grade_discounted_money,
			# 	'promotion_result': promotion_result,
			# 	'integral_sale_id': r.integral_sale_id,
			# 	'delivery_item_id': r.order_id,
			# 	'db_model': product_db_model
			# }
			#
			# delivery_item_product = DeliveryItemProduct.get({
			# 	'corp': self.corp,
			# 	'product_info': delivery_item_product_info
			# })
			delivery_item_products.append(delivery_item_product)

		delivery_item_id2products = {}

		# 把delivery_item_product分配给相应出货单
		for product in delivery_item_products:
			if product.delivery_item_id in delivery_item_id2products:
				delivery_item_id2products[product.delivery_item_id].append(product)
			else:
				delivery_item_id2products[product.delivery_item_id] = [product]

		for delivery_item in delivery_items:
			# todo 使用get兼容历史错误数据，需要修正数据库
			# 历史订单中的错误数据修复 - 自营订单有出货单记录，但没对应的mall_order_has_product记录
			# select o1.id,o1.origin_order_id,o1.created_at,h.id from mall_order  as o1  left join  mall_order_has_product as h on o1.id=h.order_id where o1.origin_order_id>0 and h.id is null order by o1.created_at;

			# delivery_item.products = delivery_item_id2products[delivery_item.id]
			delivery_item.products = delivery_item_id2products.get(delivery_item.id, [])

			# 排序
			delivery_item.products.sort(lambda x, y: cmp(x.context["index"], y.context["index"]))
