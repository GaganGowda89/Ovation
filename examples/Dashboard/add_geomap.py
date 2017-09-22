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
vis_id = 'geomapfoo'
vis_title = 'GeoMap Sentiment'
vis_source_loc = field_map['geography'][0] # there is only one
vis_source_sum = field_map['summary'][0] # there is only one


vis = {
    "title" : vis_title,
    "visState" : "{\"title\":\""+vis_title+"\",\"type\":\"tile_map\",\"params\":{\"mapType\":\"Scaled Circle Markers\",\"isDesaturated\":true,\"addTooltip\":true,\"heatMaxZoom\":0,\"heatMinOpacity\":0.1,\"heatRadius\":25,\"heatBlur\":15,\"legendPosition\":\"topright\",\"mapZoom\":2,\"mapCenter\":[0,0],\"wms\":{\"enabled\":false,\"url\":\"https://basemap.nationalmap.gov/arcgis/services/USGSTopo/MapServer/WMSServer\",\"options\":{\"version\":\"1.3.0\",\"layers\":\"0\",\"format\":\"image/png\",\"transparent\":true,\"attribution\":\"Maps provided by USGS\",\"styles\":\"\"}}},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"top_hits\",\"schema\":\"metric\",\"params\":{\"field\":\""+vis_source_sum+"\",\"aggregate\":\"average\",\"size\":1,\"sortField\":\""+vis_source_sum+"\",\"sortOrder\":\"desc\"}},{\"id\":\"2\",\"enabled\":true,\"type\":\"geohash_grid\",\"schema\":\"segment\",\"params\":{\"field\":\""+vis_source_loc+"\",\"autoPrecision\":true,\"useGeocentroid\":true,\"precision\":2}}],\"listeners\":{}}",
    "uiStateJSON" : "{\"mapZoom\":6,\"mapCenter\":[52.520008,13.404954]}",
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
      "title": "zee",
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
