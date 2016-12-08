# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required

from business.mall.label.product_label import ProductLabel
from business.mall.corporation_factory import CorporationFactory


class AProductLable(api_resource.ApiResource):
	"""
	商品标签
	"""
	app = 'mall'
	resource = 'product_label'

	@param_required(['label_group_id', 'label_name'])
	def put(args):
		"""
		创建标签
		"""
		result = ProductLabel.create({
			'label_group_id': args['label_group_id'],
			'label_name': args['label_name']
		})
		if isinstance(result, basestring):
			return (500, result)
		else:
			return {
				'label': {
					'id': result.id,
					'name': result.name,
					'label_group_id': result.label_group_id,
					'created_at': result.created_at.strftime('%Y-%m-%d %H:%M:%S')
				}
			}

	@param_required(['label_id:int'])
	def delete(args):
		"""
		删除标签
		"""
		weizoom_corp = CorporationFactory.get_weizoom_corporation()
		weizoom_corp.product_label_repository.delete_labels([args['label_id']])

		return {}

