from lxml import html
import requests
import ast

r = requests.get('http://yandex.ru/images/search?text=marilyn%20manson%20the%20pale%20emperor')
tree = html.fromstring(r.text)
classes = tree.xpath('//div[@class="serp-item__preview"]/a[@class="serp-item__link"]/@onmousedown')[0][6:-2]
link = ast.literal_eval(classes)[1].get('href')
print(link)

# or you can use
classes = tree.xpath('//div[@class="serp-item__preview"]/a[@class="serp-item__link"]/@onmousedown')
for i in classes:
  link = ast.literal_eval(i[6:-2])[1].get('href')
  if link.lower().find('emperor') != -1:
    print(link)

