from elasticsearch import Elasticsearch
from datetime import datetime
from random import randint
from random import uniform
from time import sleep
import requests
import json
import csv
import re

#TODO : select correct values
#host = 'http://192.168.54.25:9200'
host = 'http://localhost:9200'
interactive = True
bignumber = 10000 # because we can't get 'all' results :-(
false = False # this makes sense when using JSON data

es = Elasticsearch([host])


r = requests.get(host+'/.kibana/_search?q=*&size='+str(bignumber))
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
#tit = tit.sub('[*]', '', line)
if tit[-1] == '*':
    tit = tit[:-1]

# Index id
sid = index_ids[selected]

print('Selected ID: '+index_ids[selected])


print('Contacting '+host+'/'+tit)
r = requests.get(host+'/'+tit) 
j = r.json();
doc_types = j[tit]['mappings'].keys()
doc_type_names = [];
for dt in doc_types:
    doc_type_names.append(dt);

print('Available fields:')
for dt in doc_types:
    print('    '+str(doc_type_names.index(dt))+'. '+dt)

print('Select doc type number:')
if interactive:
    selected = int(input('>'))
else:
    selected = 0
doc_type = doc_type_names[selected]

print('Select metadata number:')
if interactive:
    selected = int(input('>'))
else:
    selected = 1
doc_meta = doc_type_names[selected]


print()

print('Summary:')
print('    Index title: '+tit)
print('    Index ID: '+sid)
print('    Doc type: '+doc_type)
print('    Doc meta: '+doc_meta)
print('')

# Looking for all field types
r = requests.get(host+'/'+tit+'/'+doc_meta+'/_search?q=*&size='+str(bignumber))
tags = r.json()['hits']['hits']
field_type = set()
for element in tags:
    for key in element['_source'].keys():
        field_type.add(key)

# Creating a map [field type] -> [set(field_names)]
field_map = {}
for ft in field_type:
    r = requests.get(host+'/'+tit+'/'+doc_meta+'/_search?q='+ft+':*&size='+str(bignumber))
    tags = r.json()['hits']['hits']
    field_map[ft] = []
    for element in tags:
        field_map[ft].append(element['_source'][ft])
    
# Display the information which was extracted
print('Field types:')
for ft in field_type:
    print('    '+ft)

print('Field map:')
for ft in field_map.keys():
    print('    '+ft+' has fields:')
    for fn in field_map[ft]:
        print('        '+fn)

# We can first create a visualisation to. Here, I will illustrate with a
# gauge, but we'll have to adapt it to our own
# stuff
vis_id = 'avgsent1'
vis_title = 'Sentiment Gauge'
vis_field = field_map['summary'][0] # there is only one

vis = {
    "title" : vis_title,
    "visState" : "{\"title\":\""+vis_title+"\",\"type\":\"gauge\",\"params\":{\"addTooltip\":true,\"addLegend\":true,\"gauge\":{\"verticalSplit\":false,\"extendRange\":true,\"percentageMode\":false,\"gaugeType\":\"Arc\",\"gaugeStyle\":\"Full\",\"backStyle\":\"Full\",\"orientation\":\"vertical\",\"colorSchema\":\"Green to Red\",\"gaugeColorMode\":\"Labels\",\"colorsRange\":[{\"from\":0,\"to\":2},{\"from\":2,\"to\":3},{\"from\":3,\"to\":5}],\"invertColors\":true,\"labels\":{\"show\":true,\"color\":\"black\"},\"scale\":{\"show\":true,\"labels\":false,\"color\":\"#333\"},\"type\":\"meter\",\"style\":{\"bgWidth\":0.9,\"width\":0.9,\"mask\":false,\"bgMask\":false,\"maskBars\":50,\"bgFill\":\"#eee\",\"bgColor\":false,\"subText\":\"\",\"fontSize\":60,\"labelColor\":true}}},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"avg\",\"schema\":\"metric\",\"params\":{\"field\":\""+vis_field+"\",\"customLabel\":\"Avg\"}}],\"listeners\":{}}",
    "uiStateJSON" : "{\"vis\":{\"colors\":{\"2 - 3\":\"#F9BA8F\"},\"defaultColors\":{\"0 - 2\":\"rgb(165,0,38)\",\"2 - 3\":\"rgb(255,255,190)\",\"3 - 5\":\"rgb(0,104,55)\"}}}",
    "description" : "",
    "version" : 1,
    "kibanaSavedObjectMeta" : {
        "searchSourceJSON" : "{\"index\":\""+sid+"\",\"query\":{\"match_all\":{}},\"filter\":[]}"
    }
}


es.index(index='.kibana', doc_type='visualization', body=vis, id=vis_id)


# The next step is to create a dashboard with the gauge.
dashboard_id = 'dashythedashboardfoo'
dashboard_json = {
      "title": "Ohai",
      "hits": 0,
      "description": "",
      "panelsJSON": "[{\"col\":1,\"id\":\""+vis_id+"\",\"panelIndex\":1,\"row\":1,\"size_x\":6,\"size_y\":3,\"type\":\"visualization\"}]",
      "optionsJSON": "{\"darkTheme\":false}",
      "uiStateJSON": "{}",
      "version": 1,
      "timeRestore": false,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"filter\":[{\"query\":{\"match_all\":{}}}],\"highlightAll\":true,\"version\":true}"
      }
    }
es.index(index='.kibana', doc_type='dashboard', body=dashboard_json, id=dashboard_id)
