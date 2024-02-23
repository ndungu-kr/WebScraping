import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider2"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        # Get all the books on the main page
        books = response.css('article.product_pod')

        for book in books:
            # get the url for the book in loop
            relative_url = book.css('h3 a ::attr(href)').get()

            # building url for detailed book page
            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url

            # follow the url into the detailed book page and parse using parse_book_page function
            yield response.follow(book_url, callback=self.parse_book_page)

        # generating the next page url
        next_page = response.css('li.next a ::attr(href)').get()

        # creating next page url
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page

            # loading the next page and calling parse function to get all books on page
            yield response.follow(next_page_url, callback= self.parse)

    # this function gets specified details from book page
    def parse_book_page(self, response):

        # gets all data in the table row  
        table_rows = response.css("table tr")
        
        yield {
            'url': response.url,
            'title': response.css('.product_main h1::text').get(),
            'product_type': table_rows[1].css('td ::text').get(),
            'price_excl_tax': table_rows[2].css('td ::text').get(),
            'price_incl_tax': table_rows[3].css('td ::text').get(),
            'tax': table_rows[4].css('td ::text').get(),
            'availability': table_rows[5].css('td ::text').get(),
            'num_reviews': table_rows[6].css('td ::text').get(),
            'stars' : response.css('p.star-rating').attrib['class'],
            'category' : response.xpath('//*[@id="default"]/div/div/ul/li[3]/a/text()').get(),
            'description' : response.xpath('//*[@id="content_inner"]/article/p/text()').get(),
            'price' : response.css('p.price_color ::text').get(),
        }
