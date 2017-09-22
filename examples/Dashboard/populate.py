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



class Review:
    def __init__(self, row):
        # Best random date generator ever
        fake_date = ('2017-%02d-%02dT%02d:%02d:%09.6f' % (randint(1,8), randint(1,28), randint(1,23), randint(0,59), uniform(0,59)))
        print(fake_date)
        sentiment = (score(row[0], row[1]) + score(row[2], row[3]) - int(row[4]) - int(row[5]) - int(row[6]) - int(row[7]) + score(row[9], row[8]) + score(row[11], row[10])) / 4
        sentiment = int(sentiment)
        sentiment = max(1, sentiment)
        sentiment = min(sentiment, 5)
        print('    '+str(sentiment))
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
           'sentiment': sentiment,
           'location': str(uniform(-90, 90))+','+str(uniform(-180, 180))
        }
        
        age = 20
        if randint(0,1) == 0:
            age = int(30 - uniform(0, 12**0.5)**2)
        else:
            age = int(30 + uniform(0, 51**0.5)**2)
        print(age)
        self.data['age'] = age


        if randint(0, 100) < 47:
            self.data['gender'] = 'm'
        else:
            self.data['gender'] = 'f'
        
        src_id = randint(0, 100)
        if src_id < 27:
            self.data['source'] = 'Facebook'
        elif src_id < 48:
            self.data['source'] = 'Twitter'
        elif src_id < 89:
            self.data['source'] = 'Homepage'
        elif src_id < 101:
            self.data['source'] = 'Google+'
        
        
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
            self.data['pos_food'] = randint(3,4)
            self.data['neg_food'] = randint(0,1)
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
            self.data['neg_food'] = randint(3,4)
            self.data['pos_food'] = randint(0,1)
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
            self.data['pos_friendly'] = randint(3,4)
            self.data['neg_friendly'] = randint(0,1)


es = Elasticsearch([host])
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
    'age' : ['demography', 'reviewer_age', 'number'],
    'sentiment' : ['summary', 'number'],
    'location' : ['geography'],
    'gender' : ['demography', 'reviewer_gender', 'text'],
    'source' : ['source', 'text']
}

count=0
for key in types.keys():
    row = types[key]
    for value in row:
        print('        "'+value+'" : "'+key+'"')
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
        #sleep(uniform(0,2))
        
print('done')
