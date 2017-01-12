Frature:客户设置默认发货人
	#每个账号新建的第一个发货人自动设为默认
Background:
	Given jobs登录系统
	When jobs新增发货人
		"""
		[{
		"shipper":"aini",
		"area":['江苏省','南京市','栖霞区'],
		"particular_address":"文昌东路437号",
		"post_code":"02134",
		"business_name":"爱伲咖啡",
		"mobile_num":"13813984402",
		"remark":"测试"
		}}
		"""
	Then jobs查看发货人列表
		|shipper|mobile_num |        area        |particular_address|post_code|operate|
		|aini(默认)|13813984402|江苏省-南京市-栖霞区|   文昌东路437号  |  02134  |删除 删除|

	When jobs新增发货人	
		"""
		[{
		"shipper":"tuxiaobao",
		"area":['江苏省','南京市','玄武区'],
		"particular_address":"玄武路127号",
		"post_code":"02134",
		"business_name":"土小宝食品",
		"mobile_num":"13813984405",
		"remark":"测试1"
		}]
		"""
	Then jobs 查看发货人列表
		|shipper|mobile_num |        area        |particular_address|post_code|operate|
		|aini(默认)|13813984402|江苏省-南京市-栖霞区|   文昌东路437号  |  02134  |删除 删除|
		|tuxiaobao|13813984405|江苏省-南京市-玄武区|  玄武路127号   |  02134  |设为默认 删除 删除|
@gaia @set_defult_shipper
Scenario:1 客户设置默认发货人
	Given jobs登录系统
	When jobs设置默认发货人
		"""
		['tuxiaobao']
		"""
	Then jobs查看发货人列表
		|shipper|mobile_num |        area        |particular_address|post_code|operate|
		|aini|13813984406|江苏省-南京市-鼓楼区|   文昌东路437号  |  02134  |设为默认 编辑 删除|
		|tuxiaobao(默认)|13813984405|江苏省-南京市-玄武区|  玄武路127号   |  02134  | 编辑 删除|