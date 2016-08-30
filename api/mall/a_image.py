# -*- coding: utf-8 -*-
import json

from eaglet.core import api_resource
from eaglet.decorator import param_required
from eaglet.core import watchdog
from eaglet.core.exceptionutil import unicode_full_stack

from business.mall.image import Image
from business.mall.image_factory import ImageFactory


class AImage(api_resource.ApiResource):
	'''
	图片
	'''
	app = 'mall'
	resource = 'image'

	@param_required(['owner_id', 'image_id'])
	def get(args):
		'''
		图片
		'''
		params = args
		opt = {
			'owner_id': params['owner_id'],
			'image_id': params['image_id']
		}
		return Image.from_id(opt)

	@param_required(['owner_id', 'group_id', 'image_path', 'width', 'height'])
	def post(args):
		'''
		添加图片 利用工厂类@生成器
		'''
		params = args
		print '============-----------', args
		image_factory = ImageFactory.create()
		opt = {
			'owner_id': args['owner_id'],
			'group_id': args['group_id'],
			'image_path': args['image_path'],
			'width': args['width'],
			'height': args['height']
		}
		image_factory.save(opt)
		return {}

