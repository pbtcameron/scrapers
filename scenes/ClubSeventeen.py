import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class ClubseventeenSpider(BaseSceneScraper):
    name = 'ClubSeventeen'
    network = 'ClubSeventeen'

    start_urls = [
        'https://www.clubseventeen.com',
        'https://www.clubsweethearts.com'
    ]

    selector_map = {
        'title': "//div[@class='top']/h3[@class='dvd-title mb-0 mt-0']/span/text()",
        'description': ".video-info > .bottom > p::text",
        'date': "//div[@class='video-info']//p[contains(@class,'letter-space-1') and contains(@class, 'mt-10')]/b/following-sibling::text()",
        'performers': "//div[@class='video-info']/div[@class='middle']/p[@class='mt-10']/a/text()",
        'tags': "//div[@class='top']/div[@class='item-tag mt-5']/a/span/text()",
        'image': ".static-video-wrapper .video-item::attr(data-image)",
        'external_id': 'slug=(.+)',
        'pagination': '/videos.php?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.css('.list_item .thumb .video-link::attr(href)').getall()
        for link in scenes:
            if re.search(self.get_selector_map('external_id'), link) is not None:
                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene)