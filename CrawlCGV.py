import requests
from bs4 import BeautifulSoup as bs
import unicodedata


# Each Korean letters occupy 2 spaces.
# Reform a string containing Korean letters, with a fixed width, alignment and padding.
def reform_kor(string, width, align='<', fill=' '):
    count = (width - sum(1 + (unicodedata.east_asian_width(c) in "WF")
                         for c in string))
    return {
        '>': lambda s: fill * count + s,
        '<': lambda s: s + fill * count,
        '^': lambda s: fill * (count // 2) + s + fill * (count // 2 + count % 2)
    }[align](string)


# Print using a customized format.
def formatted_print(widths, *strings):
    assert all(width[0] in ['>', '<', '^'] and width[1:].isdigit() for width in widths), \
        'Width should start ">", "<", or "^" followed by an integer.'

    if len(widths) is not len(strings):
        print('Lengths of width list and string list do not match.')
        print('Output will not show unmatched elements from the last.')

    n_max = min(len(widths), len(strings))
    line = ''

    for i in range(n_max):
        line += reform_kor(strings[i], int(widths[i][1:]), widths[i][0])

    print(line)


# Get title from a 'div' block.
def get_title(div):
    return div.find('strong', {'class': 'title'}).text


# Get booking rate from a 'div' block.
def get_booking_rate(div, trim=False):
    string = div.find('strong', {"class": "percent"}).span.text
    if trim:
        string = string.replace('%', '')
    return string


# Get egg discount rate from a 'div' block.
def get_egg_discount(div, trim=False):
    string = div.find('div', {"class": "egg-gage small"}).find('span', {"class": "percent"}).text
    if trim:
        string = string.replace('%', '')
    return string


# Get the number of likes from a 'div' block.
def get_likes(div, trim=False):
    string = div.find('span', {"class": "like"}).find('span', {"class": "count"}).strong.i.text
    if trim:
        string = string.replace(',', '')
    return string


def get_movie_chart(url):
    # Query the url and return the web site content: single line.
    request = requests.get(url)
    content = request.content

    # BeautifulSoup parses the html to a readable form: lengthy.
    html = bs(content, 'html.parser')

    # Each movie is encapsulated by a 'li' block.
    # Some of 'li' blocks are grouped by a 'ol' block.
    ol_list = html.find_all('ol')
    chart = []

    for ol in ol_list:
        chart.extend(ol.find_all('li'))

    return chart


def page2dict():
    # CGV Movie Chart
    mov_list = get_movie_chart('http://www.cgv.co.kr/movies/?ft=0')
    movie_dict = {}

    align_width = ['<15', '>10', '>20', '>10']
    formatted_print(align_width, 'Title', 'Booking', 'Egg_discount', 'Likes')
    for mov in mov_list:
        # Ignore ranking. We can sort according to the booking rate.
        div = mov.find('div', {"class": "box-contents"})

        # Some 'li' blocks are empty. Skip them.
        if div is not None:
            title = get_title(div)
            booking_rate = get_booking_rate(div)
            egg_discount = get_egg_discount(div)
            likes = get_likes(div, trim=True)

            formatted_print(align_width, title, booking_rate, egg_discount, likes)
            movie_dict[title] = {'booking_rate': booking_rate, 'egg_discount': egg_discount, 'likes': likes}

    return movie_dict


# import scrapy
# https://stackoverflow.com/questions/27753232/scrapy-extract-links-and-text
# http://doc.scrapy.org/en/latest/topics/spiders.html
# https://github.com/etilelab/WebCrawlingStudy
# class myItem(scrapy.Item):
#     name = scrapy.Field()
#     link = scrapy.Field()


# class MySpider(scrapy.Spider):
#     name = 'cgv.co.kr'
#     allowed_domains = ['cgv.co.kr']

    # def start_requests(self):
    #     yield scrapy.Request('http://www.cgv.co.kr/movies/?ft=0', self.parse)               # Current
    #     yield scrapy.Request('http://www.cgv.co.kr/movies/pre-movies.aspx', self.parse)     # Coming soon

    # def parse(self, response):
    #     for sel in response.xpath('//tr//td/a'):
    #         item = myItem()
    #         item['name'] = sel.xpath('text()').extract()
    #         item['link'] = sel.xpath('@href()').extract()

            # yield item


if __name__ == '__main__':
    movies = page2dict()
    # for key, value in movies.items():
    #     print(key, value)
