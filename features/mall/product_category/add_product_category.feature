Feature: 添加商品分组
"""
	Jobs能通过管理系统为管理商城添加的"商品分组"
"""

@mall @mall.product @mall.product_category @hermes
Scenario:1 添加商品分组
	Jobs添加一组"商品分组"后，"商品分组列表"会按照添加的顺序倒序排列

	Given jobs登录系统
	When jobs添加商品分组
		"""
		[{
			"name": "分组1"
		}, {
			"name": "分组2"
		}, {
			"name": "分组3"
		}]
		"""
	Then jobs能获取商品分组列表
		"""
		[{
			"name": "分组1"
		}, {
			"name": "分组2"
		}, {
			"name": "分组3"
		}]
		"""
	Given bill登录系统
	Then bill能获取商品分组列表
		"""
		[]
		"""

@ignore
Scenario:2 添加商品时选择分组，能在分组中看到该商品
	Jobs添加一组"商品分组"后，"商品分组列表"会按照添加的顺序倒序排列

	Given jobs登录系统
	When jobs已添加商品分组
		"""
		[{
			"name": "分组1"
		}, {
			"name": "分组2"
		}, {
			"name": "分组3"
		}]
		"""
	Given jobs已添加商品
		#东坡肘子(有分组，上架，无限库存，多轮播图), 叫花鸡(无分组，下架，有限库存，单轮播图)
		"""
		[{
			"name": "东坡肘子",
			"status": "待售",
			"categories": "分组1,分组2",
			"model": {
				"models": {
					"standard": {
						"price": 11.12,
						"stock_type": "无限"
					}
				}
			}
		}, {
			"name": "叫花鸡",
			"status": "待售",
			"categories": "分组1",
			"model": {
				"models": {
					"standard": {
						"price": 12.00,
						"stock_type": "有限",
						"stocks": 3
					}
				}
			}
		}, {
			"name": "水晶虾仁",
			"status": "待售",
			"categories": "",
			"model": {
				"models": {
					"standard": {
						"price": 3.00
					}
				}
			}
		}]
		"""
	Then jobs能获取商品分组列表
		"""
		[{
			"name": "分组1",
			"products": [{
				"name": "叫花鸡",
				"display_price": 12.00,
				"status": "待售"
			}, {
				"name": "东坡肘子",
				"display_price": 11.12,
				"status": "待售"
			}]
		}, {
			"name": "分组2",
			"products": [{
				"name": "东坡肘子",
				"display_price": 11.12,
				"status": "待售"
			}]
		}, {
			"name": "分组3",
			"products": []
		}]
		"""
