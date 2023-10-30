import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMatureNLSpider(BaseSceneScraper):
    name = 'MatureNL'
    network = 'Mature NL'
    parent = 'Mature NL'
    site = 'Mature NL'

    start_urls = [
        'https://www.mature.nl',
    ]
    selector_map = {
        'title': '//h1/text()',
        'description': '//meta[@name="description"]/@content',
        'date': '//span[contains(@title, "Release")]/following-sibling::span[contains(@class, "val-m")][1]/text()',
        're_date': r'(\d{1,2}-\d{1,2}-\d{4})',
        'date_formats': ['%d-%m-%Y'],
        'duration': '//span[contains(@title, "length")]/following-sibling::span[contains(@class, "val-m")][1]/text()',
        'image': '//span[@id="spnPageUpdateTrailer"]//img/@data-src|//video/@poster',
        'image_blob': True,
        'performers': '//div[@class="box-cnt"]//div[@class="grid-tile-model"]/div[@class="name"]/span/text()',
        'tags': '//div[@class="box-cnt"]//a[contains(@href, "/niche/")]/text()',
        'external_id': r'update\/(\d+)\/',
        'trailer': '',
        'pagination': '/en/updates/%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="grid-item"]')
        for scene in scenes:
            scenedate = scene.xpath('./div/div//div[contains(@class, "fs-small")]/div[@class="overflow"]/text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r'(\d{1,2}-\d{1,2}-\d{4})', scenedate)
                if scenedate:
                    meta['date'] = self.parse_date(scenedate.group(1), date_formats=['%d-%m-%Y']).strftime('%Y-%m-%d')

            performers = scene.xpath('.//div[@class="card-subtitle"]/a/text()')
            if performers:
                performers_temp = performers.getall()
                performers = []
                for performer in performers_temp:
                    if re.search(r'\(.*?\)', performer):
                        performer = re.sub(r'\(.*?\)', '', performer)
                    performer = performer.strip()
                    performers.append(performer)
                if performers:
                    meta['performers'] = performers

            scene = scene.xpath('./div/div/a/@href').get()
            if "/update/" in scene:
                try:
                    sceneid = re.search(r'\/update\/(\d+)', scene).group(1)
                except Exception:
                    print(scene)
            if "upid=" in scene:
                sceneid = re.search(r'upid=(\d+)', scene).group(1)
            scene = "https://www.mature.nl/en/update/" + sceneid.strip() + "/"
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers2 = []
        if performers:
            for performer in performers:
                print(f"Performer Base: '{performer}'")
                if re.search(r'\(.*?\)', performer):
                    print(f"Performer 1: {performer}")
                    performer = re.sub(r'\(.*?\)', '', performer)
                    print(f"Performer 2: {performer}")
                performer = performer.strip()
                performers2.append(performer)
        return performers2

    def get_image(self, response):
        image = super().get_image(response)
        if not image:
            image = response.xpath(
                r'//div[@class="box-cnt"]//a[@class="mfp-image"]/@href'
            )
            if image:
                image = image.get().strip()
            else:
                image = ''
        return image

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date'))
        if date:
            date = date.get()
        if not date or not re.search(r'(\d{1,2}-\d{1,2}-\d{4})', date):
            date = response.xpath(
                r'//div[@class="container update-bg-container"]'
                '/div[@class="box"][1]/div[@class="box-cnt"]/div[1]')
            if date:
                date = date.get()
        if date and re.search(r'(\d{1,2}-\d{1,2}-\d{4})', date):
            date = self.get_from_regex(date, 're_date')
            if 'date_formats' in self.get_selector_map():
                date_formats = self.get_selector_map('date_formats')
            else:
                None
            return self.parse_date(date, date_formats=date_formats).isoformat()

    def get_title(self, response):
        title = super().get_title(response)
        if "watch this scene exclusively" in title.lower():
            newtitle = response.xpath(r'//div[@class="box-cnt"]'
                                      '//div[@class="grid-tile-model"]'
                                      '/div[@class="name"]/span/text()')
            if newtitle:
                newtitle = newtitle.getall()
                newtitle = " and ".join(newtitle)
                title = newtitle.strip()
        return self.cleanup_title(title)
