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
            if field_name != 'desciption':
                # asigning the stripped field name back to the field name 
                value = adapter.get(field_name)
                adapter[field_name] = value.strip()

        # Switching items in the Category and Product type fields into lowercase
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()

        # Converting the price into float
        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace('£', '')
            adapter[price_key] = float(value)

        # Removing text from availability and keeping exact number only 
        availability_string = adapter.get('')
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
