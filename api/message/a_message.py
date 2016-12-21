# -*- coding: utf-8 -*-

from eaglet.core import api_resource
from eaglet.decorator import param_required
from eaglet.core import watchdog
from eaglet.core.exceptionutil import unicode_full_stack

from business.station_message.message import Message
from business.station_message.message_repository import MessageRepository
from business.station_message.message_attachment_repository import MessageAttachmentRepository


class AMessage(api_resource.ApiResource):
	"""
	商品分类
	"""
	app = "message"
	resource = "message"

	@param_required(['id'])
	def get(args):
		# corp = args['corp']
		# messages = corp.message_repository.get_messages()
		msgrepo = MessageRepository()
		message = msgrepo.get_message(args['id'])
		msg_att_repo = MessageAttachmentRepository()
		attachments = msg_att_repo.get_message_attachments(args['id'])
		data = {
			'id': message.id,
			'title': message.title,
			'content': message.content,
			'attachments': attachments,
			'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
		}

		return {
			'message': data
		}

	@param_required(['corp_id', 'title', 'content', '?attachments:json'])
	def put(args):
		message = Message.create({
			'title': args['title'],
			'content': args['content'],
			'attachments': args['attachments']
		})
		return {
			'id': message.id
		}

	@param_required(['id', 'title', 'content', '?attachments:json'])
	def post(args):
		message = MessageRepository().get_message(args['id'])

		message.update(args['title'], args['content'], args['attachments'])

		return {}

	@param_required(['id'])
	def delete(args):
		MessageRepository().delete_message(args['id'])
		return {}
