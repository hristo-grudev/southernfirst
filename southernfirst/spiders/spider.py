import re

import scrapy

from scrapy.loader import ItemLoader

from ..items import SouthernfirstItem
from itemloaders.processors import TakeFirst


class SouthernfirstSpider(scrapy.Spider):
	name = 'southernfirst'
	start_urls = ['https://www.southernfirst.com/blog']

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//ul[@class="pagination"]//a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//div[@class="small-12 columns"]/div/div/h3//text()[normalize-space()]').get()
		description = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "sf-Long-text", " " ))]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//h3/following-sibling::div[1]/text()').get()
		date = re.findall(r'[A-Za-z]{3}\s\d{1,2},\s\d{4},\s\d{2}:\d{2}\s[A-Z]{2}', date) or ['']

		item = ItemLoader(item=SouthernfirstItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date[0])

		return item.load_item()
