# -*- coding: utf-8 -*-
import json

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.common.page_info import PageInfo
from business.mall.corporation_factory import CorporationFactory
from business.product.encode_product_service import EncodeProductService

class APooledProducts(api_resource.ApiResource):
	"""
	商品池中商品集合
	"""
	app = "product"
	resource = "pooled_products"

	@param_required(['corp_id'])
	def get(args):
		corp = args['corp']
		fill_options = json.loads(args.get('fill_options', '{}'))
		target_page = PageInfo.create({
			"cur_page": int(args.get('cur_page', 1)),
			"count_per_page": int(args.get('count_per_page', 10))
		})
		options = {
			'order_options': ['display_index', '-onshelf_time', '-id']
		}
		if fill_options:
			options['request_source'] = 'unshelf_consignment'
		else:
			fill_options = {
				'with_product_model': True,
				'with_model_property_info': True,
				'with_shelve_status': True,
				'with_supplier_info': True,
				'with_classification': True,
				'with_product_label': True,
			}
		
		filters = json.loads(args.get('filters', '{}'))
		products, pageinfo = corp.product_pool.get_products(target_page, fill_options, options, filters)

		encode_product_service = EncodeProductService.get(corp)
		datas = []
		for product in products:
			base_info = encode_product_service.get_base_info(product)
			data = {
				'id': product.id,
				'name': base_info['name'],
				"create_type": base_info['create_type'],
				"image": base_info['thumbnails_url'],
				"bar_code": base_info['bar_code'],
				"display_index": base_info['display_index'],
			}
			if fill_options.get('with_product_model'):
				models_info = encode_product_service.get_models_info(product)
				data['models_info'] = models_info
				if product.is_use_custom_model:
					data['stock_type'] = 'combined'
					data['stocks'] = -1
					data['price'] = 'todo'
				else:
					standard_model = product.standard_model
					data['stock_type'] = standard_model.stock_type
					data['stocks'] = standard_model.stocks
					data['price'] = standard_model.price
			if fill_options.get('with_supplier_info'):
				supplier = encode_product_service.get_supplier_info(product)
				data['supplier'] = supplier
			if fill_options.get('with_classification'):
				classifications = encode_product_service.get_classifications(product)
				data['classifications'] = classifications
			# if fill_options.get('with_image'):
			# 	image_info = encode_product_service.get_image_info(product)
			if fill_options.get('with_product_label'):
				labels = encode_product_service.get_labels(product)
				data['labels'] = labels

			datas.append(data)

		return {
			'pageinfo': pageinfo.to_dict(),
			'products': datas
		}
		