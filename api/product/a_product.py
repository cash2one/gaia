# -*- coding: utf-8 -*-


from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.product.product_factory import ProductFactory
from business.product.update_product_service import UpdateProductService


class AProduct(api_resource.ApiResource):
	"""
	商品
	"""
	app = "product"
	resource = "product"

	@staticmethod
	def __get_models_info(product):
		"""
		获得商品的models_info数据
		"""
		models_info = {
			'is_use_custom_model': False,
			'standard_model': None,
			'custom_models': [],
			'used_system_model_properties': None
		}
		models_info['is_use_custom_model'] = product.is_use_custom_model

		standard_model = product.standard_model
		if standard_model:
			models_info['standard_model'] = {
				"id": standard_model.id,
				"name": standard_model.name,
				"price": standard_model.price,
				"purchase_price": standard_model.purchase_price,
				"weight": standard_model.weight,
				"stock_type": standard_model.stock_type,
				"stocks": standard_model.stocks,
				"user_code": standard_model.user_code
			}
		else:
			models_info['standard_model'] = None
		
		custom_models = product.custom_models
		if custom_models:
			for custom_model in custom_models:
				models_info['custom_models'].append({
					"id": custom_model.id,
					"name": custom_model.name,
					"price": custom_model.price,
					"purchase_price": custom_model.purchase_price,
					"weight": custom_model.weight,
					"stock_type": custom_model.stock_type,
					"stocks": custom_model.stocks,
					"user_code": custom_model.user_code,
					"property_values": custom_model.property_values,
					"property2value": custom_model.property2value
				})
		else:
			models_info['custom_models'] = []

		return models_info

	@staticmethod
	def __get_image_info(product):
		"""
		获得商品的image_info数据
		"""
		image_info = {
			'thumbnails_url': product.thumbnails_url,
			'images': []
		}

		images = image_info['images']
		for image in product.swipe_images:
			images.append({
				"url": image['url'],
				#"link_url": image['link_url'],
				"width": image['width'],
				"height": image['height']
			})

		return image_info

	@staticmethod
	def __get_categories(product):
		"""
		获得商品的category集合
		"""
		categories = []
		for category in product.categories:
			categories.append({
				"id": category['id'],
				"name": category['name']
			})

		return categories

	@staticmethod
	def __get_pay_info(product):
		return {
			'is_use_online_pay_interface': product.is_use_online_pay_interface,
			'is_use_cod_pay_interface': product.is_use_cod_pay_interface
		}

	@staticmethod
	def __get_properties(product):
		data = []
		for product_property in product.properties:
			data.append({
				"name": product_property['name'],
				"value": product_property['value']
			})

		return data

	@staticmethod
	def __get_logistics_info(product):
		data = {
			'postage_type': product.postage_type,
			'unified_postage_money': product.unified_postage_money
		}

		return data

	@staticmethod
	def __get_supplier_info(product):
		"""
		获得商品的supplier集合
		"""
		supplier = product.supplier
		if not supplier:
			return None

		data = {
			'id': supplier.id,
			'name': supplier.name,
			'type': supplier.type,
			'divide_type_info': None,
			'retail_type_info': None
		}

		if supplier.is_divide_type():
			divide_info = supplier.get_divide_info()
			data['divide_type_info'] = {
				"id": divide_info.id,
				"divide_money": divide_info.divide_money,
				"basic_rebate": divide_info.basic_rebate,
				"rebate": divide_info.rebate
			}
		elif supplier.is_retail_type():
			retail_info = supplier.get_retail_info()
			data['retail_info'] = {
				"id": retail_info.id,
				"rebate": retail_info.rebate
			}

		return data

	@staticmethod
	def __get_classifications(product):
		"""
		获得商品的classification集合
		"""
		datas = []

		if len(product.classification_lists) > 0:
			classification_list = product.classification_lists[0]
			
			for classification in classification_list:
				datas.append({
					"id": classification.id,
					"level": classification.level,
					"name": classification.name
				})

		return datas

	@param_required(['corp_id', 'id'])
	def get(args):
		corp = args['corp']
		ids = [args['id']]
		fill_options = {
			'with_category': True,
			'with_image': True,
			'with_product_model': True,
			'with_model_property_info': True,
			'with_property': True,
			'with_supplier_info': True,
			'with_classification': True
		}
		products = corp.product_pool.get_products_by_ids(ids, fill_options)
		if len(products) == 0:
			return {}
		else:
			product = products[0]

			data = {
				"id": product.id,
				"base_info": {
					"name": product.name,
					"type": product.type,
					"create_type": product.create_type,
					"bar_code": product.bar_code,
					"min_limit": product.min_limit,
					"is_enable_bill": product.is_enable_bill,
					"promotion_title": product.promotion_title,
					"detail": product.detail,
					"is_member_product": product.is_member_product,
					"sync_at": product.sync_at.strftime('%Y-%m-%d %H:%M') if product.create_type == 'sync' else None,
					"created_at": product.created_at.strftime('%Y-%m-%d %H:%M')
				},
				"categories": AProduct.__get_categories(product),
				"image_info": AProduct.__get_image_info(product),
				"models_info": AProduct.__get_models_info(product),
				"pay_info": AProduct.__get_pay_info(product),
				'properties': AProduct.__get_properties(product),
				"logistics_info": AProduct.__get_logistics_info(product),
				"supplier": AProduct.__get_supplier_info(product),
				"classifications": AProduct.__get_classifications(product)
			}

			return data

	@param_required(['corp_id', 'base_info', 'models_info', 'image_info', 'logistics_info', 'pay_info', 'categories', 'properties'])
	def put(args):
		"""
		创建商品
		@return:
		"""
		product_data = args
		product_factory = ProductFactory.get(args['corp'])
		product_factory.create_product(product_data)

		return {}

	@param_required(['corp_id', 'id', 'base_info', 'models_info', 'image_info', 'logistics_info', 'pay_info', 'categories', 'properties'])
	def post(args):
		product_data = args
		product_id = product_data['id']
		update_product_service = UpdateProductService.get(args['corp'])
		update_product_service.update_product(product_id, product_data)

		return {}

	@param_required(['ids'])
	def delete(args):
		pass
