# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.common.page_info import PageInfo

class APreProducts(api_resource.ApiResource):
	"""
	待审核商品集合
	"""
	app = "mall"
	resource = "pre_products"

	@param_required(['corp_id'])
	def get(args):
		corp = args['corp']
		page_info = PageInfo.create({
			"cur_page": int(args.get('cur_page', 1)),
			"count_per_page": int(args.get('count_per_page', 15))
		})
		pageinfo, pre_products = corp.pre_product_repository.filter(args, page_info)

		rows = []

		for pre_product in pre_products:
			rows.append({
				'id': pre_product.id,
				'owner_id': corp.id,
				'classification_id': pre_product.classification_id,
				'product_name': pre_product.product_name,
				'customer_name': '', #?
				'total_sales': 0, #TODO 获取已入库商品的销量
				'product_status': pre_product.status_text,
				'product_status_value': 0, #?
				'classification_name_nav': pre_product.classification_nav,
				'is_update': pre_product.is_update,
				'customer_from_text': '', #?
				'refuse_reason': pre_product.refuse_reason,
				'label_names': [] #TODO商品标签
			})

		return {
			'rows': rows,
			'pageinfo': pageinfo.to_dict()
		}
		