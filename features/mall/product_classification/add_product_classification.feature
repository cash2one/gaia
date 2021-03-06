Feature: 添加商品分类
"""
	Jobs能通过管理系统为管理商城添加的"商品分类"
"""

@gaia @mall @mall.product @mall.product_classification
Scenario:1 添加无商品的商品分类

	Given weizoom登录系统
	When weizoom添加商品分类
		"""
		[{
			"分类11": [{
                "分类21": []
            },{
                "分类22": []
            },{
                "分类23": [{
                    "分类31": []
                }]
            }]
		},{
			"分类12": [{
				"分类24": []
			}]
		},{
			"分类13": []
		}]
		"""
	Then weizoom查看商品分类列表
		|classfication_name|      operation      |
		|   分类11  |修改,删除,配置标签|
		|   分类12  |修改,删除,配置标签|
		|   分类13  |修改,删除,配置标签|

	Then weizoom能获得'分类11'的子分类集合
		"""
		["分类21", "分类22", "分类23"]
		"""
	Then weizoom能获得'分类23'的子分类集合
		"""
		["分类31"]
		"""
	Then weizoom能获得'分类21'的子分类集合
		"""
		[]
		"""
