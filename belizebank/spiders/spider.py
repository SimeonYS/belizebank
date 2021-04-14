import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbelizebankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BbelizebankSpider(scrapy.Spider):
	name = 'belizebank'
	start_urls = ['https://www.belizebank.com/corporate-governance/about-us/in-the-news/']

	def parse(self, response):
		articles = response.xpath('//div[@class="vc_col-sm-12 vc_gitem-col vc_gitem-col-align-"]')
		for article in articles:
			post_links = article.xpath('.//a[@title="Read more"]/@href').get()
			title = article.xpath('.//h4/text()').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(title=title))

	def parse_post(self, response, title):
		date = response.xpath('//div[@class="col-md-12"]/p/em/text()').get()
		if not date:
			date = "Date not stated in article"
		content = response.xpath('//div[@class="col-md-12"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BbelizebankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
