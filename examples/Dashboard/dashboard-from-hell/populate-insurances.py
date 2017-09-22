from elasticsearch import Elasticsearch
from datetime import datetime
from random import randint
from random import uniform
from time import sleep
from math import sqrt
from math import ceil
from math import exp
import json
import csv



# DEFINITIONS
host = 'http://localhost:9200'

def score(a, b):
    a = int(a)
    b = int(b)
    if a == 0 and b == 0:
        return 2
    return ceil(a-b+4)


insurance_plans = ['Afterlife insurance', 'Car insurance', 'Health insurance']

class Review:
    def __init__(self, row):
        # Best random date generator ever
        fake_date = ('2017-%02d-%02dT%02d:%02d:%09.6f' % (randint(1,8), randint(1,28), randint(1,23), randint(0,59), uniform(0,59)))
        print(fake_date)
        sentiment = (score(row[0], row[1]) + score(row[2], row[3]) - int(row[4]) + score(row[5], row[6]) + int(row[7]) - int(row[8])) / 3
        sentiment = int(sentiment)
        sentiment = max(1, sentiment)
        sentiment = min(sentiment, 5)
        print('    '+str(sentiment))
        self.data = {
           'pos_price': int(row[0]),
           'bad_price': int(row[1]),
           'pos_policy': int(row[2]),
           'bad_policy': int(row[3]),
           'bad_coverage': int(row[4]),
           'pos_contact': int(row[5]),
           'bad_contact': int(row[6]),
           'fast_resp': int(row[7]),
           'slow_resp': int(row[8]),
           'claim_rejection': int(row[9]),
           'feedback': row[13],
           'feedback_length': int(row[14]),
           'date': fake_date,
           'age': randint(18, 81),
           'sentiment': sentiment,
           'location': str(uniform(-90, 90))+','+str(uniform(-180, 180)),
           'plan': insurance_plans[randint(0,len(insurance_plans)-1)]
        }
        
        age = 20
        if randint(0,1) == 0:
            age = int(40 - uniform(0, 22**0.5)**2)
        else:
            age = int(40 + uniform(0, 31**0.5)**2)
        print(age)
        self.data['age'] = age


        if randint(0, 100) < 47:
            self.data['gender'] = 'm'
        else:
            self.data['gender'] = 'f'
        
        src_id = randint(0, 100)
        if src_id < 27:
            self.data['source'] = 'Facebook'
        elif src_id < 37:
            self.data['source'] = 'Twitter'
        elif src_id < 72:
            self.data['source'] = 'Webpage'
        elif src_id < 75:
            self.data['source'] = 'Google+'
        elif src_id < 101:
            self.data['source'] = 'Blogs'
        
        
        # Location-based 
        fun = randint(0,20)
        if fun == 0:
            # germany - likes all food
            p = randint(0,2)
            if p==0:
                geox = 51 + uniform(0, sqrt(2))**2
                geoy = 11 + uniform(0, sqrt(3))**2
            if p==1:
                geox = 51 + uniform(0, sqrt(2))**2
                geoy = 8.5 + uniform(0, sqrt(3))**2
            if p==2:
                geox = 49 + uniform(0, sqrt(2))**2
                geoy = 10 + uniform(0, sqrt(3))**2
            self.data['location']=str(geox)+','+str(geoy)
            self.data['pos_policy'] = randint(3,4)
            self.data['bad_policy'] = randint(0,1)
        if fun == 1:
            # france - dislikes all food
            p = randint(0,2)
            if p==0:
                geox = 47 + uniform(0, sqrt(4))**2
                geoy = 3 + uniform(0, sqrt(4))**2
            if p==1:
                geox = 47 + uniform(0, sqrt(4))**2
                geoy =  0 + uniform(0, sqrt(4))**2
            if p==2:
                geox = 44 + uniform(0, sqrt(4))**2
                geoy =  3 + uniform(0, sqrt(4))**2
            self.data['location']=str(geox)+','+str(geoy)
            self.data['bad_price'] = randint(3,4)
            self.data['pos_price'] = randint(0,1)
        if fun == 2:
            # italy - they are very friendly
            p = randint(0,2)
            if p==0:
                geox = 45 + uniform(0, sqrt(1))**2
                geoy = 10.5 + uniform(0, sqrt(1))**2
            if p==1:
                geox = 43.8 + uniform(0, sqrt(1))**2
                geoy = 11.6 + uniform(0, sqrt(1))**2
            if p==2:
                geox = 42.6 + uniform(0, sqrt(1))**2
                geoy = 12.7 + uniform(0, sqrt(1))**2
            self.data['location']=str(geox)+','+str(geoy)
            self.data['pos_contact'] = randint(3,4)
            self.data['bad_contact'] = randint(0,1)


es = Elasticsearch([host])
es.indices.delete(index='insurance', ignore=[400,404])
settings = {
    "mappings": {
        "opinion": {
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
es.indices.create(index='insurance', body=settings)


# Types:
#  - reason
#  - positive/negative
#  - demography [for filters?]
#  - geography [single value per review]
#  - timeline [single value per review]
#  - number/text
types = {
    'pos_price': ['positive', 'reason', 'number'],
    'bad_price': ['negative', 'reason', 'number'],
    'pos_policy': ['positive', 'reason', 'number'],
    'bad_policy': ['negative', 'reason', 'number'],
    'bad_coverage': ['negative', 'reason', 'number'],
    'pos_contact': ['positive', 'reason', 'number'],
    'bad_contact': ['negative', 'reason', 'number'],
    'fast_resp': ['positive', 'reason', 'number'],
    'slow_resp': ['negative', 'reason', 'number'],
    'claim_rejection': ['negative', 'reason', 'number'],
    'date' : ['timeline'],
    'age' : ['demography', 'reviewer_age', 'number'],
    'sentiment' : ['summary', 'number'],
    'location' : ['geography'],
    'gender' : ['demography', 'reviewer_gender', 'text'],
    'source' : ['source', 'text'],
    'plan' : ['filter', 'text']
}

count=0
for key in types.keys():
    row = types[key]
    for value in row:
        print('        "'+value+'" : "'+key+'"')
        es.index(index='insurance', doc_type='field_types', body={value : key})


with open('gt_amazon.csv', 'rt', encoding='utf8') as csvfile:
    data = csv.reader(csvfile, delimiter='\t')
    
    first = True
    for row in data:
        if first:
            first = False
            continue
        review = Review(row)
        es.index(index='insurance', doc_type='opinion', body=review.data)
        #sleep(uniform(0,2))
        
print('done')
