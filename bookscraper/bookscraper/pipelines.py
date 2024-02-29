# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscraperPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        # Strip all whitespace from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != 'description':
                # asigning the stripped field name back to the field name 
                value = adapter.get(field_name)
                adapter[field_name] = value.strip()

        # Switching items in the Category and Product type fields into lowercase
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()

        # Converting the prices into float values
        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace('£', '')
            adapter[price_key] = float(value)

        # Removing text from availability and keeping exact number only 
        availability_string = adapter.get('availability')
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            adapter['availability'] = 0
        else:
            availability_array = split_string_array[1].split(' ')
            adapter['availability'] = int(availability_array[0])

        # converting number of reviews to an integer
        num_reviews_string = adapter.get('num_reviews')
        adapter['num_reviews'] = int(num_reviews_string)

        # converting star rating into integer values
        star_string = adapter.get('stars')
        star_rating_array = star_string.split(' ')
        star_text_value = star_rating_array[1].lower()
        if star_text_value == "zero":
            adapter['stars'] = 0
        elif star_text_value == "one":
            adapter['stars'] = 1
        elif star_text_value == "two":
            adapter['stars'] = 2
        elif star_text_value == "three":
            adapter['stars'] = 3
        elif star_text_value == "four":
            adapter['stars'] = 4
        elif star_text_value == "five":
            adapter['stars'] = 5

        return item


import mysql.connector

class SaveToMySQLPipeline:
    """ 
    This will only create the db and input data,
    functionality for check for duplicates has not been implemented,
    so if the "books" table exists, it will append rows.
    """
    
    def __init__(self):
        self.conn = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'password',
            database = 'books'
        )

        # Create cursor, used to execute commands
        self.cur = self.conn.cursor()

        # Create books table if it doesn't exist
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id int NOT NULL auto_increment, 
            url VARCHAR(255),
            title text,
            upc VARCHAR(255),
            product_type VARCHAR(255),
            price_excl_tax DECIMAL,
            price_incl_tax DECIMAL,
            tax DECIMAL,
            price DECIMAL,
            availability INTEGER,
            num_reviews INTEGER,
            stars INTEGER,
            category VARCHAR(255),
            description text,
            PRIMARY KEY (id)
        )
        """)

    def process_item(self, item, spider):

        ## Define insert statement
        self.cur.execute(""" insert into books (
            url, 
            title, 
            upc, 
            product_type, 
            price_excl_tax,
            price_incl_tax,
            tax,
            price,
            availability,
            num_reviews,
            stars,
            category,
            description
            ) values (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
                )""", (
            item["url"],
            item["title"],
            item["upc"],
            item["product_type"],
            item["price_excl_tax"],
            item["price_incl_tax"],
            item["tax"],
            item["price"],
            item["availability"],
            item["num_reviews"],
            item["stars"],
            item["category"],
            str(item["description"][0])
        ))

        # ## Execute insert of data into database
        self.conn.commit()
        return item
    
    def close_spider(self, spider):

        ## Close cursor & connection to database 
        self.cur.close()
        self.conn.close()