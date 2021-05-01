import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
import dateparser


class PornprosSpider(BaseSceneScraper):
    name = 'MetArtNetwork'
    network = 'metart'
    start_urls = [
        "https://www.sexart.com/",
        "https://www.metart.com/",
        "https://www.vivthomas.com/",
        "https://www.metartx.com/",
        "https://www.thelifeerotic.com/",
        "https://www.errotica-archives.com/",
        "https://www.alsscan.com",
        "https://www.eroticbeauty.com",
        "https://www.eternaldesire.com",
        "https://www.lovehairy.com",
        "https://www.rylskyart.com",
        "https://www.stunning18.com",
        "https://www.thelifeerotic.com",
    ]

    selector_map = {
        'external_id': 'movie\\/(.+)',
        'pagination': '/api/movies?galleryType=MOVIE&first=60&page=%s&staffSelectionHead=false&tabId&order=DATE&direction=DESC&type=MOVIE'
    }

    max_pages = 100

    def get_scenes(self, response):
        movies = response.json()['galleries']
        for movie in movies:
            res = re.search('movie/(\\d+)/(.+)', movie['path'])
            yield scrapy.Request(
                url=self.format_link(
                    response, '/api/movie?name=' + res.group(2) + '&date=' + res.group(1)),
                callback=self.parse_scene)

    def parse_scene(self, response):
        movie = response.json()
        item = SceneItem()
        item['title'] = movie['name']
        item['description'] = movie['description']
        item['performers'] = []

        for performer in movie['models']:
            item['performers'].append(performer['name'])

        if 'coverCleanImagePath' in movie:
            item['image'] = self.format_link(
                response, movie['coverCleanImagePath'])

        if 'splashImagePath' in movie:
            item['image'] = self.format_link(
                response, movie['splashImagePath'])

        item['date'] = dateparser.parse(movie['publishedAt']).isoformat()
        item['tags'] = movie['tags']
        item['trailer'] = self.format_url(
            response.url, '/api/m3u8/' + movie['UUID'] + '.m3u8')
        item['site'] = self.get_site(response)
        item['url'] = self.format_link(response, movie['path'])
        item['network'] = self.network
        res = re.search('movie/(\\d+)/(.+)', movie['path'])
        item['id'] = res.group(2)

        yield item