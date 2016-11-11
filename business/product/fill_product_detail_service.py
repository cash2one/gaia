# coding=utf-8
# -*- utf-8 -*-
from eaglet.decorator import param_required

from bdem import msgutil
from business import model as business_model

from business.product.product import Product
from business.product.model.product_model_generator import ProductModelGenerator
from db.mall import models as mall_models
from gaia_conf import TOPIC

import settings


class FillProductDetailService(business_model.Service):
	"""
	对商品集合批量进行详情填充的服务
	"""
	def __fill_shelve_status(self, corp, products):
		"""
		填充商品货架状态相关细节
		"""
		if len(products) == 0:
			return

		product_ids = [product.id for product in products]
		id2product = dict([(product.id, product) for product in products])
		for p in mall_models.ProductPool.select().dj_where(product_id__in=product_ids):
			product = id2product[p.product_id]
			if p.status == mall_models.PP_STATUS_ON:
				product.set_shelve_type('on_shelf')
			elif p.status == mall_models.PP_STATUS_OFF:
				product.set_shelve_type('off_shelf')
			elif p.status == mall_models.PP_STATUS_ON_POOL:
				product.set_shelve_type('in_pool')
			else:
				product.set_shelve_type('deleted')
			product.display_index = p.display_index

	def __fill_model_detail(self, corp, products, is_enable_model_property_info=False):
		"""填充商品规格相关细节
		向product中添加is_use_custom_model, models, used_system_model_properties三个属性
		"""
		first_product = products[0]
		if first_product.standard_model or first_product.custom_models:
			#已经完成过填充，再次进入，跳过填充
			return

		#TODO2: 因为这里是静态方法，所以目前无法使用product.context['corp']，构造基于Object的临时解决方案，需要优化
		product_model_generator = ProductModelGenerator.get(corp)
		product_model_generator.fill_models_for_products(products, is_enable_model_property_info)

	def __fill_category_detail(self, product_ids, id2product):
		"""填充商品分类信息相关细节
		"""

		# 获取product关联的category集合
		for key, product in id2product.items():
			product.categories = []

		relations = mall_models.CategoryHasProduct.select().dj_where(product_id__in=product_ids).order_by('id')
		catagory_ids = [relation.category_id for relation in relations]
		categories = list(mall_models.ProductCategory.select().dj_where(id__in=catagory_ids).order_by('id'))

		id2category = dict([(category.id, category) for category in categories])
		for relation in relations:
			category_id = relation.category_id
			product_id = relation.product_id
			if not category_id in id2category:
				# 微众商城分类，在商户中没有
				continue
			category = id2category[category_id]
			id2product[product_id].categories.append({
				'id': category.id,
				'name': category.name
			})

	def __fill_image_detail(self, corp, products, product_ids):
		"""
		填充商品轮播图相关细节
		"""
		id2product = dict([(product.id, product) for product in products])

		for img in mall_models.ProductSwipeImage.select().dj_where(product_id__in=product_ids):
			data = {
				'id': img.id,
				'url': '%s%s' % (settings.IMAGE_HOST, img.url) if img.url.find('http') == -1 else img.url,
				'link_url': img.link_url,
				'width': img.width,
				'height': img.height
			}
			id2product[img.product_id].swipe_images.append(data)

	def __fill_display_price(self, products):
		"""
		根据商品规格，获取商品价格
		"""
		for product in products:
			if product.is_use_custom_model:
				custom_models = product.custom_models
				if len(custom_models) == 1:
					#只有一个custom model，显示custom model的价格信息
					product_model = custom_models[0]
					product.price_info = {
						'display_price': str("%.2f" % product_model.price),
						'display_original_price': str("%.2f" % product_model.original_price),
						'display_market_price': str("%.2f" % product_model.market_price),
						'min_price': product_model.price,
						'max_price': product_model.price,
					}
				else:
					#有多个custom model，显示custom model集合组合后的价格信息
					prices = []
					market_prices = []
					for product_model in custom_models:
						if product_model.price > 0:
							prices.append(product_model.price)
						if product_model.market_price > 0:
							market_prices.append(product_model.market_price)

					if len(market_prices) == 0:
						market_prices.append(0.0)

					if len(prices) == 0:
						prices.append(0.0)

					prices.sort()
					market_prices.sort()
					# 如果最大价格和最小价格相同，价格处显示一个价格。
					if prices[0] == prices[-1]:
						price_range =  str("%.2f" % prices[0])
					else:
						price_range = '%s-%s' % (str("%.2f" % prices[0]), str("%.2f" % prices[-1]))

					if market_prices[0] == market_prices[-1]:
						market_price_range = str("%.2f" % market_prices[0])
					else:
						market_price_range = '%s-%s' % (str("%.2f" % market_prices[0]), str("%.2f" % market_prices[-1]))

					# 最低价
					min_price = prices[0]
					# 最高价
					max_price = prices[-1]

					product.price_info = {
						#'display_price': price_range,
						#'display_original_price': price_range,
						'display_price': str("%.2f" % min_price),
						'display_original_price': str("%.2f" % min_price),
						'display_market_price': market_price_range,
						'min_price': min_price,
						'max_price': max_price,
					}
			else:
				standard_model = product.standard_model
				if standard_model:
					product.price_info = {
						'display_price': str("%.2f" % standard_model.price),
						'display_original_price': str("%.2f" % standard_model.original_price),
						'display_market_price': str("%.2f" % standard_model.market_price),
						'min_price': standard_model.price,
						'max_price': standard_model.price,
					}
				else:
					product.price_info = {
						'display_price': str("%.2f" % 0),
						'display_original_price': str("%.2f" % 0),
						'display_market_price': str("%.2f" % 0),
						'min_price': 0,
						'max_price': 0,
					}

	def __fill_property_detail(self, corp, products, product_ids):
		"""
		填充商品属性相关细节
		"""
		id2product = dict([(product.id, product) for product in products])

		for product_property in mall_models.ProductProperty.select().dj_where(product_id__in=product_ids):
			product = id2product[product_property.product_id]
			product.properties.append({
				"name": product_property.name,
				"value": product_property.value
			})

	def __fill_supplier_detail(self, corp, products, product_ids):
		"""
		填充供应商相关细节
		"""
		supplier_ids = list(set([product.supplier_id for product in products if product.supplier_id != 0]))
		supplier2products = {}
		for product in products:
			supplier2products.setdefault(product.supplier_id, []).append(product)
		
		suppliers = corp.supplier_repository.get_suppliers_by_ids(supplier_ids)
		for supplier in suppliers:
			for product in supplier2products[supplier.id]:
				product.supplier = supplier

	def __fill_classification_detail(self, corp, products, product_ids, id2product):
		"""
		填充供应商相关细节
		"""
		relations = mall_models.ClassificationHasProduct.select().dj_where(product_id__in=product_ids)

		classifications = corp.product_classification_repository.get_product_classifications()
		id2classification = dict([(classification.id, classification) for classification in classifications])

		for relation in relations:
			classification_list = []
			product = id2product[relation.product_id]
			classification = id2classification[relation.classification_id]
			classification_list.append(classification)

			while True:
				if classification.father_id == 0:
					break

				classification = id2classification[classification.father_id]
				classification_list.append(classification)

			classification_list.sort(lambda x,y: cmp(x.level, y.level))
			product.classification_lists.append(classification_list)

	def __fill_label_detail(self, corp, products, product_ids):
		"""
		填充商品标签的信息
		"""
		relations = mall_models.ProductHasLabel.select().dj_where(product_id__in=product_ids,
																  label_id__gt=0)
		label_ids = []
		product_id2label_ids = {}
		for relation in relations:
			label_ids.append(relation.label_id)
			product_id2label_ids.setdefault(relation.product_id, []).append(relation.label_id)

		labels = corp.product_label_repository.get_labels(label_ids)
		id2label = dict([(label.id, label)for label in labels])
		for product in products:
			product.labels = []
			if product.id not in product_id2label_ids:
				continue
			product_label_ids = product_id2label_ids[product.id]
			for label_id in product_label_ids:
				product.labels.append(id2label[label_id])

	def __fill_sales_detail(slef, corp, products, product_ids, id2product):
		"""填充商品销售情况相关细节
		"""
		for product in products:
			product.sales = 0

		for sales in mall_models.ProductSales.select().dj_where(product_id__in=product_ids):
			product_id = sales.product_id
			if id2product.has_key(product_id):
				id2product[product_id].sales = sales.sales

	def __fill_cps_promoteion_info(self, corp, products, product_ids, id2product):
		"""
		填充商品的cps推广信息
		"""
		promotion_infos = mall_models.PromoteDetail.select().dj_where(product_id__in=product_ids)
		pool_product_models = mall_models.ProductPool.select().dj_where(product_id__in=product_ids)
		id2pool_products = dict([(pool.product_id, pool) for pool in pool_product_models])
		for promotion in promotion_infos:
			product = id2product.get(promotion.product_id)
			# product_id = product_id,
			# promote_money = money,
			# promote_time_from = time_from,
			# promote_time_to = time_to,
			# promote_sale_count = sale_count,
			# promote_total_money = total_money,
			# promote_stock = stock
			pool_product_model = id2pool_products[promotion.product_id]
			promotion_info = {
				'money': promotion.promote_money,
				'time_from': promotion.promote_time_from,
				'time_to': promotion.promote_time_to,
				'sale_count': promotion.promote_sale_count,
				'total_money': promotion.promote_total_money,
				'stock': promotion.promote_stock,
				'is_cps_promotion_processed': pool_product_model.is_cps_promotion_processed,
				'id': promotion.id
			}
			product.cps_promoted_info = promotion_info

	def fill_detail(self, products, options):
		"""填充各种细节信息

		此方法会根据options中的各种填充选项，填充相应的细节信息

		@param[in] products: Product业务对象集合
		@param[in] options: 填充选项
			with_price: 填充价格信息
			with_product_model: 填充所有商品规格信息
			with_product_promotion: 填充商品促销信息
			with_image: 填充商品轮播图信息
			with_property: 填充商品属性信息
			with_selected_category: 填充选中的分类信息
			with_all_category: 填充所有商品分类详情
			with_sales: 填充商品销售详情
			with_cps_promotion_info: 填充商品cps推广信息
		"""
		if len(products) == 0:
			return

		if not options:
			return
			
		is_enable_model_property_info = options.get('with_model_property_info',False)
		product_ids = [product.id for product in products]
		id2product = dict([(product.id, product) for product in products])

		for product in products:
			product.detail_link = '/mall/product/?id=%d&source=onshelf' % product.id

		if options.get('with_price', False):
			#price需要商品规格信息
			self.__fill_model_detail(self.corp, products, is_enable_model_property_info)
			self.__fill_display_price(products)

		if options.get('with_product_model', False):
			self.__fill_model_detail(self.corp, products, is_enable_model_property_info)

		if options.get('with_shelve_status', False):
			self.__fill_shelve_status(self.corp, products)

		if options.get('with_product_promotion', False):
			Product.__fill_promotion_detail(corp, products, product_ids)

		if options.get('with_image', False):
			self.__fill_image_detail(self.corp, products, product_ids)

		if options.get('with_property', False):
			self.__fill_property_detail(self.corp, products, product_ids)

		if options.get('with_category', False):
			self.__fill_category_detail(product_ids, id2product)

		if options.get('with_supplier_info', False):
			self.__fill_supplier_detail(self.corp, products, product_ids)

		if options.get('with_classification', False):
			self.__fill_classification_detail(self.corp, products, product_ids, id2product)

		if options.get('with_sales', False):
			self.__fill_sales_detail(self.corp, products, product_ids, id2product)

		if options.get('with_product_label', False):
			self.__fill_label_detail(self.corp, products, product_ids)

		if options.get('with_cps_promotion_info', False):
			self.__fill_cps_promoteion_info(self.corp, products, product_ids, id2product)
