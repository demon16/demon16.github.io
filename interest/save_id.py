from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client.exp
collection = db.id
data = []

img_path = '/home/simon/图片/id/xxxxx.png'
with open(img_path, 'rb') as f:
    img = f.read()

xxx = {'name': 'xxxxxx', 'sex': 0, 'num': 'xxxxxxxx',
      'phone': None, 'area': 'xxxxx',
      'nation': 'xxxx', 'img': img, 'img_type': 'png'}
data.append(xxx)