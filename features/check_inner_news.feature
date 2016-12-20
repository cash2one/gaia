#author:徐梓豪 2016-12-06
feature:客户查看站内消息
	"""
	#运营新增站内消息后，客户端未读的消息数量要在分页名称后以(x)的形式体现
	#进入分页后，未读的消息按时间倒序置顶并且加粗显示
	#运营修改完消息后，客户这的消息也要修改
	#运营删除消息后，客户这的消息也要被删除
	"""
Background:
	Given manager登录管理系统
	When manager添加账号
		"""
		[{
			"login_account":"yunying",
			"password":"1",
			"real_name":"运营",
			"email":"yunying@163.com",
			"department":"CorpStaff",
			"right":"运营管理"
		},{
			"login_account":"aini",
			"password":"1",
			"real_name":"爱伲咖啡",
			"email":"aini@163.com",
			"department":"CorpStaff",
			"right":"商户操作"
		}]
		"""
	Given manager登录系统
	When manager添加分类
		"""
		[{
		"head_classify":"无",
		"classify_name":"电子数码",
		"comments":"1"
		},{
		"head_classify":"无",
		"classify_name":"生活用品",
		"comments":"1"
		},{
		"head_classify":"电子数码",
		"classify_name":"手机",
		"comments":""
		},{
		"head_classify":"电子数码",
		"classify_name":"平板电脑",
		"comments":""
		},{
		"head_classify":"电子数码",
		"classify_name":"耳机",
		"comments":""
		},{
		"head_classify":"生活用品",
		"classify_name":"零食",
		"comments":""
		},{
		"head_classify":"生活用品",
		"classify_name":"肥皂",
		"comments":""
		},{
		"head_classify":"生活用品",
		"classify_name":"清洗用品,
		"comments":""
		}]
		"""
	Given manager登录系统
	When manager新增站内消息
		"""
		[{
		"title":"每日新闻",
		"content":"今日华为获取世界范围5g标准的短码控制信道",
		"accessory":''
		},{
		"title":"新增功能介绍",
		"content":"系统目前新增新功能站内消息，系统更新功能后会在这及时更新并附上操作视频",
		"accessory":''
		},{
		"title":"商品信息管理规范",
		"content":"微众商城“上线商品”信息管理规范说明",
		"accessory":''
		}]
		"""
@mantis @news
Scenario: 用户查看站内消息
	Given aini登录系统
	When aini查看站内信息列表
		|      title     |creat_time|
		|    每日新闻    | 创建时间 |
		|  新增功能介绍  | 创建时间 |
		|商品信息管理规范| 创建时间 |
	When aini查看'每日新闻'的详情
		"""
		{
		"title":"每日新闻",
		"content":"今日华为获取世界范围5g标准的短码控制信道",
		"accessory":''
		}
		"""
	When aini查看'新增功能介绍'的详情
		"""
		{
		"title":"新增功能介绍",
		"content":"系统目前新增新功能站内消息，系统更新功能后会在这及时更新并附上操作视频",
		"accessory":''
		}
		"""
	When aini查看'商品信息管理规范'的详情
		"""
		{
		"title":"商品信息管理规范",
		"content":"微众商城“上线商品”信息管理规范说明",
		"accessory":''
		}
		"""
	Given manager登录系统
	When manager编辑站内消息'每日之声'
		"""
		[{
		"title":"每日之声",
		"content":"今日推荐：土小宝",
		"accessory":''
		}]
		"""
	Then aini查看消息列表
		|      title     |creat_time|
		|    每日之声    | 创建时间 |
		|  新增功能介绍  | 创建时间 |
		|商品信息管理规范| 创建时间 |
	Then aini查看消息'每日之声'	
		"""
		[{
		"title":"每日之声",
		"content":"今日推荐：土小宝",
		"accessory":''
		}]
		"""
	When manager删除站内消息'每日之声'
	Then aini查看站内消息列表
		|      title     |creat_time|
		|  新增功能介绍  | 创建时间 |
		|商品信息管理规范| 创建时间 |

