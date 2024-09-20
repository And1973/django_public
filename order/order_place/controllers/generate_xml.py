from django.http import HttpResponse
import csv
from io import StringIO
import diskcache as dc
import requests
from xml.etree.ElementTree import Element, tostring
import os
from django.conf import settings
cache = dc.Cache(str(settings.BASE_DIR / 'order_place' / 'controllers' / 'cache'))

def send_message(chat_id, text):
    token = 'Telegram_token'
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=data)

def download_image(image_url, filename, count):
    cache_key = filename
    cached_image_path = cache.get(cache_key)
    if cached_image_path:
        return cached_image_path
    image_path = os.path.join(settings.MEDIA_ROOT, 'images', filename)
    if not os.path.exists(image_path):
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(image_path, 'wb') as file:
                count[0] += 1
                file.write(response.content)
            return image_path
    else:
        count[1] += 1
        cache.set(cache_key, image_path)
        return image_path
    return None
    

def generate_xml(request):
    url = ("Suppliers_url")

    def fetch_and_parse_csv(url):
        response = requests.get(url)
        if response.status_code == 200:
            content = StringIO(response.content.decode('utf-8'))
            csv_reader = csv.reader(content)
            datas = list(csv_reader)
            return datas
        return None

    def get_data(url):
        cached_data = cache.get(url)
        if cached_data:
            data_source = "XML Data fetched from the cache."
            return cached_data, data_source
        else:
            data_source = "XML Data fetched from the network."
            data = fetch_and_parse_csv(url)
            if data:
                cache.set(url, data, expire = 3600)
            return data, data_source

    items, data_source = get_data(url) 
    count = [0,0]
    root = Element('items')
    for item in items[1:]:
        if int(item[2]) > 0:
            item_element = Element('item')
            
            name = Element('name')
            name.text = item[1]
            item_element.append(name)
            
            quantity = Element('quantity')
            quantity.text = item[2]
            item_element.append(quantity)

            price = Element('price')
            price.text = item[3]
            item_element.append(price)

            image_ext_url = item[7]
            image_filename = image_ext_url.split('images/')[-1]

            if download_image(image_ext_url, image_filename, count):
                image = Element('image')
                image.text = f"{request.build_absolute_uri('/media/images/')}{image_filename}"
                item_element.append(image)
            
            root.append(item_element)
    send_message(118876845, f'{data_source}\n{count[0]} pictures downloaded from Supplier\n{count[1]} pictures added to cache')
    xml_data = tostring(root, encoding='utf-8')
    return HttpResponse(xml_data, content_type='application/xml')