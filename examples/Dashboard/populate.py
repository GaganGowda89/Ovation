from elasticsearch import Elasticsearch
from datetime import datetime
from random import randint
from random import uniform
import json
import csv

# DEFINITIONS

class Review:
    def __init__(self, row):
        #fake_date = ('2017-%02d-%02d %02d:%02d:%02d:%06.3f' % (randint(1,8), randint(1,30), randint(1,23), randint(0,59), randint(0,59), uniform(0,59)))
        #print(fake_date)
        self.data = {
           'pos_food': row[0],
           'neg_food': row[1],
           'pos_location': row[2],
           'bad_location': row[3],
           'bad_hygiene': row[4],
           'renovation_needed': row[5],
           'payment_problems': row[6],
           'technical_problems': row[7],
           'neg_comfortable': row[8],
           'pos_comfortable': row[9],
           'neg_friendly': row[10],
           'pos_friendly': row[11],
           'no_category': row[12],
           'review': row[13],
           'review_length': row[14],
           'date': datetime.now(),
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
        "hotels": {
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


with open('gt_amazon.csv', 'rt', encoding='utf8') as csvfile:
    data = csv.reader(csvfile, delimiter='\t')
    
    first = True
    for row in data:
	    if first:
	        first = False
	        continue
	    review = Review(row)
	    es.index(index='hotels', doc_type='review', body=review.data)