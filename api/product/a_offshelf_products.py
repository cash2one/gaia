# -*- coding: utf-8 -*-

import json

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.product.product import Product
from business.product.product_shelf import ProductShelf
from business.common.page_info import PageInfo


class AOffshelfProducts(api_resource.ApiResource):
	"""
	待售商品集合
	"""
	app = "product"
	resource = "offshelf_products"

	@staticmethod
	def _get_models_info(product):
		"""
		获得商品的models_info数据
		"""
		models_info = {
			'is_use_custom_model': False,
			'standard_model': None,
			'custom_models': []
			#'used_system_model_properties': None
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
					"property_values": custom_model.property_values
				})
		else:
			models_info['custom_models'] = []

		return models_info

	@staticmethod
	def _get_categories(product):
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
	def _get_supplier(product):
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
	def _get_classifications(product):
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

	@param_required(['corp_id'])
	def get(args):
		corp = args['corp']
		
		target_page = PageInfo.create({
			"cur_page": int(args.get('cur_page', 1)),
			"count_per_page": int(args.get('count_per_page', 10))
		})

		products, pageinfo = corp.forsale_shelf.get_products(target_page)

		datas = []
		for product in products:
			data = {
				"id": product.id,
				"name": product.name,
				"create_type": product.create_type,
				"image": product.thumbnails_url,
				"models_info": AOffshelfProducts._get_models_info(product),
				"user_code": -1,
				"bar_code": product.bar_code,
				"categories": AOffshelfProducts._get_categories(product),
				"price": None,
				"sales": product.sales,
				"created_at": product.created_at.strftime('%Y-%m-%d %H:%M'),
				"is_use_custom_model": product.is_use_custom_model,
				"display_index": product.display_index,
				'supplier': AOffshelfProducts._get_supplier(product),
				'classifications': AOffshelfProducts._get_classifications(product)
			}

			if product.is_use_custom_model:
				data['stock_type'] = 'combined'
				data['stocks'] = -1
				data['price'] = 'todo'
			else:
				standard_model = product.standard_model
				data['stock_type'] = standard_model.stock_type
				data['stocks'] = standard_model.stocks
				data['price'] = standard_model.price

			datas.append(data)

		return {
			'pageinfo': pageinfo.to_dict(),
			'products': datas
		}

	@param_required(['corp_id', 'product_ids'])
	def put(args):
		corp = args['corp']
		product_ids = json.loads(args['product_ids'])
		corp.forsale_shelf.move_products(product_ids)

		return {}