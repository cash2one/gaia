#coding: utf8
from eaglet.core.db import models

import datetime

class User(models.Model):
	"""
	从django.contrib.auth.User迁移过来
	"""
	username = models.CharField(max_length=30)
	first_name = models.CharField(max_length=30, default='')
	last_name = models.CharField(max_length=30, default='')
	email = models.EmailField(default='')
	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True,)
	date_joined = models.DateTimeField(default=datetime.datetime.now)

	class Meta:
		db_table = 'auth_user'
		verbose_name = 'user'
		verbose_name_plural = 'users'

SYSTEM_VERSION_TYPE_BASE= 'base'
SYSTEM_VERSION_TYPE_PREMIUM = 'premium'
SYSTEM_VERSION_TYPES = (
	(SYSTEM_VERSION_TYPE_BASE, '初级版'),
	(SYSTEM_VERSION_TYPE_PREMIUM, '高级版'),
	)

USER_STATUS_NORMAL = 0
USER_STATUS_BUSY = 1
USER_STATUS_DISABLED = 2
USER_STATUSES = (
	(USER_STATUS_NORMAL, '正常'),
	(USER_STATUS_BUSY, '忙碌'),
	(USER_STATUS_DISABLED, '停用')
)
SELF_OPERATION = 0
THIRD_OPERATION = 1
OTHER_OPERATION = 2

OPERATION_TYPE = {
	SELF_OPERATION: u'自运营',
	THIRD_OPERATION: u'代运营',
	OTHER_OPERATION: u'其它'
}

WEBAPP_TYPE_MALL = 0 #普通商城
WEBAPP_TYPE_WEIZOOM_MALL = 1 #微众商城

class UserProfile(models.Model):
	"""
	用户profile
	"""
	user = models.ForeignKey(User)
	manager_id = models.IntegerField(default=0) #创建该用户的系统用户的id
	webapp_id = models.CharField(max_length=16)
	webapp_type = models.IntegerField(default=0) #商城类型
	app_display_name = models.CharField(max_length=50, verbose_name='用于显示app名称')
	is_active = models.BooleanField(default=True, verbose_name='用户是否有效')
	note = models.CharField(max_length=1024, default='')
	status = models.IntegerField(default=USER_STATUS_NORMAL)
	is_mp_registered = models.BooleanField(default=False, verbose_name='是否已经接入了公众账号')
	mp_token = models.CharField(max_length=50, verbose_name='绑定公众号使用的token')
	mp_url = models.CharField(max_length=256, verbose_name='公众号绑定的url')
	new_message_count = models.IntegerField(default=0) #新消息数
	webapp_template = models.CharField(max_length=50, default='shop') #webapp的模板
	is_customed = models.IntegerField(default=0) #是否客户自定义CSS样式：1：是；0：否
	is_under_previewed = models.IntegerField(default=0) #是否是预览模式：1：是；0：否
	expire_date_day = models.DateField(auto_now_add=True)
	force_logout_date = models.BigIntegerField(default=0)

	host_name = models.CharField(max_length=1024, default="")
	logout_redirect_to = models.CharField(max_length=1024, default="")
	system_name = models.CharField(max_length=64, default=u'微信营销管理系统', verbose_name='系统名称')
	system_version = models.CharField(max_length=16, default=SYSTEM_VERSION_TYPE_BASE, verbose_name='系统版本')

	homepage_template_name = models.CharField(max_length=250) #首页模板名
	backend_template_name = models.CharField(max_length=250) #后端页面模板名
	homepage_workspace_id = models.IntegerField(default=0) #homepage workspace的id
	#add by bert
	account_type = models.IntegerField(default=SELF_OPERATION)#帐号类型
	is_oauth = models.BooleanField(default=False) #是否授权
	#v2
	sub_account_count = models.IntegerField(default=50) #可创建的子账号的个数
	#wepage
	is_use_wepage = models.BooleanField(default=False) #是否启用wepage
	store_name = models.CharField(max_length=64, default="") #店铺名称
	class Meta(object):
		db_table = 'account_user_profile'

PLACE_ORDER = 0  # 下单
PAY_ORDER = 1  # 付款
SHIP_ORDER = 2  # 发货
SUCCESSED_ORDER = 3  # 完成
CANCEL_ORDER = 4  # 已取消


class UserOrderNotifySettings(models.Model):
	user = models.ForeignKey(User)
	emails = models.TextField(default='')  # '|'分割
	black_member_ids = models.TextField(default='')  # '|'分割，会员id
	status = models.IntegerField(default=0)
	is_active = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta(object):
		db_table = 'user_order_notify_setting'



class ZeusApp(models.Model):
	"""
	【Zeus用】ZeusApp
	"""
	name = models.CharField(max_length=20, db_index=True)
	app_key = models.CharField(max_length=50, unique=True)
	app_secret = models.CharField(max_length=50)
	is_deleted = models.BooleanField(default=False)

	class Meta(object):
		db_table = "zeus_app"


class AccessToken(models.Model):
	"""
	【Zeus用】存储access token （Weapp不应访问此库）
	"""
	access_token = models.CharField(max_length=50, unique=True) # unique implies the creation of an index
	corp_id = models.CharField(max_length=50, default='')
	used_count = models.IntegerField(default=0) # 使用过次数
	created_at = models.DateTimeField(auto_now_add=True)
	expire_time = models.DateTimeField() # 失效时间
	app = models.ForeignKey(ZeusApp)
	is_active = models.BooleanField(default=True)

	class Meta(object):
		db_table = "zeus_access_token"
