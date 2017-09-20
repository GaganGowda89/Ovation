from elasticsearch import Elasticsearch
from datetime import datetime
from random import randint
from random import uniform
from time import sleep
import json
import csv

# DEFINITIONS

class Review:
    def __init__(self, row):
        # Best random date generator ever
        fake_date = ('2017-%02d-%02dT%02d:%02d:%09.6f' % (randint(1,8), randint(1,28), randint(1,23), randint(0,59), uniform(0,59)))
        print(fake_date)
        self.data = {
           'pos_food': int(row[0]),
           'neg_food': int(row[1]),
           'pos_location': int(row[2]),
           'bad_location': int(row[3]),
           'bad_hygiene': int(row[4]),
           'renovation_needed': int(row[5]),
           'payment_problems': int(row[6]),
           'technical_problems': int(row[7]),
           'neg_comfortable': int(row[8]),
           'pos_comfortable': int(row[9]),
           'neg_friendly': int(row[10]),
           'pos_friendly': int(row[11]),
           'no_category': int(row[12]),
           'review': row[13],
           'review_length': int(row[14]),
           'date': fake_date,
           'age': randint(18, 81),
           'sentiment': randint(0, 5),
           'location': str(uniform(-90, 90))+','+str(uniform(-180, 180))
        }
        if randint(0, 1) == 0:
            self.data['gender'] = 'm'
        else:
            self.data['gender'] = 'f'
        
        src_id = randint(0, 3)
        if src_id == 0:
            self.data['source'] = 'Facebook'
        elif src_id == 1:
            self.data['source'] = 'Twitter'
        elif src_id == 2:
            self.data['source'] = 'Homepage'
        elif src_id == 3:
            self.data['source'] = 'Connected toaster'


# IMPLEMENTATION


es = Elasticsearch()
es.indices.delete(index='hotels', ignore=[400,404])
settings = {
    "mappings": {
        "review": {
            "properties": {
                "date": {
                    "type": "date"
                },
                'location': {
                    'type': 'geo_point'
                }
            }
        }
     }
}
es.indices.create(index='hotels', body=settings)


# Types:
#  - reason
#  - positive/negative
#  - demography [for filters?]
#  - geography [single value per review]
#  - timeline [single value per review]
#  - number/text
types = {
    'pos_food' : ['positive', 'reason', 'number'],
    'neg_food' : ['negative', 'reason', 'number'],
    'pos_location' : ['positive', 'reason', 'number'],
    'bad_location' : ['negative', 'reason', 'number'],
    'bad_hygiene' : ['negative', 'reason', 'number'],
    'renovation_needed' : ['negative', 'reason', 'number'],
    'payment_problems' : ['negative', 'reason', 'number'],
    'technical_problems' : ['negative', 'reason', 'number'],
    'neg_comfortable' : ['negative', 'reason', 'number'],
    'pos_comfortable' : ['positive', 'reason', 'number'],
    'neg_friendly' : ['negative', 'reason', 'number'],
    'pos_friendly' : ['positive', 'reason', 'number'],
    'date' : ['timeline'],
    'age' : ['demography', 'number'],
    'sentiment' : ['summary', 'number'],
    'location' : ['geography'],
    'gender' : ['demography', 'text'],
    'source' : ['source', 'text']
}
for key in types.keys():
    row = types[key]
    for value in row:
        print(value+' -> '+key)
        es.index(index='hotels', doc_type='meta', body={value : key})


with open('gt_amazon.csv', 'rt', encoding='utf8') as csvfile:
    data = csv.reader(csvfile, delimiter='\t')
    
    first = True
    for row in data:
        if first:
            first = False
            continue
        review = Review(row)
        es.index(index='hotels', doc_type='review', body=review.data)
        sleep(uniform(0,2))
        
print('done')
