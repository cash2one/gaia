Feature: 添加商品分类
"""
	Jobs能通过管理系统为管理商城添加的"商品分类"
"""

@mall @mall.product @mall.product_classification @hermes
Scenario:1 添加无商品的商品分类

	Given jobs登录系统
	When jobs添加商品分类
		"""
		{
			"分类11": {
				"分类21": null,
				"分类22": null,
				"分类23": {
					"分类31": null
				}
			},
			"分类12": {
				"分类24": null
			},
			"分类13": null
		}
		"""
	Then jobs能获取商品分类列表
		"""
		{
			"分类11": {
				"分类21": null,
				"分类22": null,
				"分类23": {
					"分类31": null
				}
			},
			"分类12": {
				"分类24": null
			},
			"分类13": null
		}
		"""
	Then jobs能获得'分类11'的子分类集合
		"""
		["分类21", "分类22", "分类23"]
		"""
	Then jobs能获得'分类23'的子分类集合
		"""
		["分类31"]
		"""
	Then jobs能获得'分类21'的子分类集合
		"""
		[]
		"""
