# -*- coding: utf-8 -*-
import json

from eaglet.core import watchdog

from business import model as business_model
from business.product.product import Product
from db.mall import models as mall_models
from eaglet.decorator import param_required


class ProductFactory(business_model.Service):
	"""
	商品工厂
	"""
	def __create_product(self, base_info, image_info, logistics_info, pay_info):
		product = mall_models.Product.create(
			owner=self.corp.id,
			name=base_info.get('name', '').strip(),
			promotion_title=base_info.get('promotion_title', '').strip(),
			bar_code=base_info.get('bar_code', '').strip(),
			thumbnails_url=image_info.get('thumbnails_url', '').strip(),
			pic_url='',
			detail=base_info.get('detail', '').strip(),
			type=base_info.get('type', mall_models.PRODUCT_DEFAULT_TYPE),
			is_use_online_pay_interface=pay_info["is_use_online_pay_interface"],
			is_use_cod_pay_interface=pay_info["is_use_cod_pay_interface"],
			postage_type=logistics_info['postage_type'],
			postage_id=logistics_info.get('postage_id', 0),
			unified_postage_money=logistics_info['unified_postage_money'],
			stocks=base_info['min_limit'],
			is_member_product=base_info["is_member_product"],
			supplier=base_info.get('supplier_id', 0),
			purchase_price=base_info.get('purchase_price', 0.0),
			is_enable_bill=base_info['is_enable_bill'],
			is_delivery=base_info.get('is_delivery', 'false') == 'true',
			limit_zone_type=int(logistics_info.get('limit_zone_type', '0')),
			limit_zone=int(logistics_info.get('limit_zone_id', '0'))
		)
		
		return product

	def __add_product_to_categories(self, product, category_ids):
		"""
		将商品加入到多个商品分组中
		"""
		if len(category_ids) == 0:
			return

		for category_id in category_ids:
			mall_models.CategoryHasProduct.create(
				category = category_id,
				product = product.id
			)

	def __add_product_to_classification(self, product, base_info):
		"""
		将商品加入到多个商品分类中
		"""
		classification_id = int(base_info.get('classification_id', 0))
		if classification_id == 0:
			return

		mall_models.ClassificationHasProduct.create(
			classification = classification_id,
			product_id = product.id,
			woid = self.corp.id,
			display_index = 0
		)

	def __set_product_models(self, product, models_info):
		# 处理standard商品规格
		is_delete_standard_model = models_info.get('is_use_custom_model', False)
		corp_id = self.corp.id

		#在任何情况下，都创建一个的standard model
		if is_delete_standard_model:
			mall_models.ProductModel.create(
				owner=corp_id,
				product=product.id,
				name='standard',
				is_standard=True,
				price=0.0,
				purchase_price=0.0,
				weight=0,
				stock_type=mall_models.PRODUCT_STOCK_TYPE_UNLIMIT,
				stocks=-1,
				user_code='',
				is_deleted=True
			)
		else:
			standard_model = models_info['standard_model']
			mall_models.ProductModel.create(
				owner=corp_id,
				product=product.id,
				name='standard',
				is_standard=True,
				price=standard_model['price'],
				purchase_price=standard_model['purchase_price'],
				weight=standard_model['weight'],
				stock_type=mall_models.PRODUCT_STOCK_TYPE_UNLIMIT if standard_model['stock_type'] == 'unlimit' else mall_models.PRODUCT_STOCK_TYPE_LIMIT,
				stocks=standard_model['stocks'],
				user_code=standard_model['user_code'],
				is_deleted=False
			)

		# 处理custom商品规格
		custom_models = models_info['custom_models']
		for custom_model in custom_models:
			product_model = mall_models.ProductModel.create(
				owner=corp_id,
				product=product.id,
				name=custom_model['name'],
				is_standard=False,
				purchase_price=custom_model.get('purchase_price', 0),
				price=custom_model['price'],
				weight=custom_model['weight'],
				stock_type=mall_models.PRODUCT_STOCK_TYPE_UNLIMIT if custom_model['stock_type'] == 'unlimit' else mall_models.PRODUCT_STOCK_TYPE_LIMIT,
				stocks=custom_model['stocks'],
				user_code=custom_model['user_code']
			)

			for property in custom_model['properties']:
				mall_models.ProductModelHasPropertyValue.create(
					model=product_model,
					property_id=property['property_id'],
					property_value_id=property['property_value_id']
				)

	def __add_images_to_product(self, product, image_info):
		"""
		设置商品图片
		"""
		images = image_info['images']
		if len(images) == 0:
			return

		for swipe_image in images:
			if swipe_image['width'] and swipe_image['height']:
				mall_models.ProductSwipeImage.create(
					product=product.id,
					url=swipe_image['url'],
					width=swipe_image['width'],
					height=swipe_image['height']
				)

	def __add_properties_to_product(self, product, properties):
		"""
		设置商品属性
		"""
		for product_property in properties:
			mall_models.ProductProperty.create(
				owner=self.corp.id,
				product=product.id,
				name=product_property['name'],
				value=product_property['value']
			)

	def create_product(self, args):
		"""
		创建自营商品
		"""
		base_info = json.loads(args['base_info'])
		models_info = json.loads(args['models_info'])
		image_info = json.loads(args['image_info'])
		logistics_info = json.loads(args['logistics_info'])
		pay_info = json.loads(args['pay_info'])
		categories = json.loads(args['categories'])
		properties = json.loads(args['properties'])

		product = self.__create_product(base_info, image_info, logistics_info, pay_info)
		self.__add_product_to_categories(product, categories)
		self.__add_product_to_classification(product, base_info)
		self.__add_images_to_product(product, image_info)
		self.__set_product_models(product, models_info)
		self.__add_properties_to_product(product, properties)

		corp = self.corp
		#将商品放入product pool
		corp.product_pool.add_products([product.id])
		#将商品放入待售shelf
		corp.forsale_shelf.add_products([product.id])

		return product

	def create_consignment_product(self, args):
		"""
		创建代售商品
		"""
		corp = self.corp
		#将代售商品放入product pool
		corp.product_pool.add_consignment_products([product.id])
		#将代售商品放入待售shelf
		corp.forsale_shelf.add_products([product.id])

		return product
