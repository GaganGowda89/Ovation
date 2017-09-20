from elasticsearch import Elasticsearch
from datetime import datetime
from random import randint
from random import uniform
from time import sleep
import requests
import json
import csv

#TODO : select correct value
interactive = False

es = Elasticsearch()

gauge = {
    "title" : "Second gauge",
    "visState" : "{\"title\":\"Second gauge\",\"type\":\"gauge\",\"params\":{\"addTooltip\":true,\"addLegend\":true,\"gauge\":{\"verticalSplit\":false,\"extendRange\":true,\"percentageMode\":false,\"gaugeType\":\"Arc\",\"gaugeStyle\":\"Full\",\"backStyle\":\"Full\",\"orientation\":\"vertical\",\"colorSchema\":\"Green to Red\",\"gaugeColorMode\":\"Labels\",\"colorsRange\":[{\"from\":0,\"to\":1},{\"from\":1,\"to\":3},{\"from\":3,\"to\":5}],\"invertColors\":false,\"labels\":{\"show\":true,\"color\":\"black\"},\"scale\":{\"show\":true,\"labels\":false,\"color\":\"#333\"},\"type\":\"meter\",\"style\":{\"bgWidth\":0.9,\"width\":0.9,\"mask\":false,\"bgMask\":false,\"maskBars\":50,\"bgFill\":\"#eee\",\"bgColor\":false,\"subText\":\"\",\"fontSize\":60,\"labelColor\":true}}},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"avg\",\"schema\":\"metric\",\"params\":{\"field\":\"bad_location\"}}],\"listeners\":{}}",
    "uiStateJSON" : "{\"vis\":{\"defaultColors\":{\"0 - 1\":\"rgb(0,104,55)\",\"1 - 3\":\"rgb(255,255,190)\",\"3 - 5\":\"rgb(165,0,38)\"}}}",
    "description" : "",
    "version" : 1,
    "kibanaSavedObjectMeta" : {
        "searchSourceJSON" : "{\"index\":\"AV6fFbfxY5xqZshhffm7\",\"query\":{\"match_all\":{}},\"filter\":[]}"
    }
}
#es.index(index='.kibana', doc_type='visualization', body=gauge)

import json
r = requests.get('http://localhost:9200/.kibana/_search?q=*') 

j = r.json();

content = j['hits']['hits']

index_titles=[]
index_ids=[]
for data in content:
    print('Type: '+data['_type'])
    if data['_type'] == 'index-pattern':
        print('    Title: '+data['_source']['title'])
        print('       id: '+data['_id'])
        index_titles.append(data['_source']['title'])
        index_ids.append(data['_id'])

print('Select index number:')
for title in index_titles:
    print('    '+str(index_titles.index(title))+'. '+title)

if interactive:
    selected = int(input('>'))
else:
    selected = 0

# Index title
tit = index_titles[selected]

# Index id
sid = index_ids[selected]

print('Selected ID: '+index_ids[selected])



r = requests.get('http://localhost:9200/'+tit) 
j = r.json();
doc_types = j[tit]['mappings'].keys()

print('Select doc type number:')
for dt in doc_types:
    print('    '+str(doc_types(dt))+'. '+dt)

if interactive:
    selected = int(input('>'))
else:
    selected = 0
