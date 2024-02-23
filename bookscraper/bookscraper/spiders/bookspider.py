import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        # Get all the books on page
        books = response.css('article.product_pod')

        # looping through books to get book details and printing to terminal 
        for book in books:
            yield {
                'name' : book.css('h3 a::text').get(),
                'price' : book.css('.product_price .price_color::text').get(),
                'url' : book.css('h3 a').attrib['href']
            }

        # generating the next page url
        next_page = response.css('li.next a ::attr(href)').get()

        # creating next page url
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page

            # loading the next page and calling parse function 
            yield response.follow(next_page_url, callback= self.parse)
