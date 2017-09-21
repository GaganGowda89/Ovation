from elasticsearch import Elasticsearch
from datetime import datetime
from random import randint
from random import uniform
from time import sleep
import requests
import json
import csv

#TODO : select correct values
host = 'http://localhost:9200'
interactive = False
bignumber = 10000 # because we can't get 'all' results :-(

es = Elasticsearch()


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

# Index id
sid = index_ids[selected]

print('Selected ID: '+index_ids[selected])



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
# print('Field types:')
# for ft in field_type:
    # print('    '+ft)

# print('Field map:')
# for ft in field_map.keys():
    # print('    '+ft+' has fields:')
    # for fn in field_map[ft]:
        # print('        '+str(fn))

#We can first create a visualisation to. Here, I will illustrate with a
#gauge, but we'll have to adapt it to our own
#stuff
vis_id = 'sentimentgauge'
vis_title = 'My gauge'
vis_source_field = field_map['summary'][0] # there is only one

print(vis_source_field)
vis = {
    "title" : vis_title,
    "visState" : "{\""+vis_title+"\":\"TITLE\",\"type\":\"gauge\",\"params\":{\"addTooltip\":true,\"addLegend\":true,\"Super gauge\":{\"verticalSplit\":false,\"extendRange\":true,\"percentageMode\":false,\"gaugeType\":\"Arc\",\"gaugeStyle\":\"Full\",\"backStyle\":\"Full\",\"orientation\":\"vertical\",\"colorSchema\":\"Green to Red\",\"gaugeColorMode\":\"Labels\",\"colorsRange\":[{\"from\":0,\"to\":1},{\"from\":1,\"to\":3},{\"from\":3,\"to\":5}],\"invertColors\":false,\"labels\":{\"show\":true,\"color\":\"black\"},\"scale\":{\"show\":true,\"labels\":false,\"color\":\"#333\"},\"type\":\"meter\",\"style\":{\"bgWidth\":0.9,\"width\":0.9,\"mask\":false,\"bgMask\":false,\"maskBars\":50,\"bgFill\":\"#eee\",\"bgColor\":false,\"subText\":\"\",\"fontSize\":60,\"labelColor\":true}}},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"avg\",\"schema\":\"metric\",\"params\":{\"field\":\""+vis_source_field+"\"}}],\"listeners\":{}}",
    "uiStateJSON" : "{\"vis\":{\"defaultColors\":{\"0 - 1\":\"rgb(0,104,55)\",\"1 - 3\":\"rgb(255,255,190)\",\"3 - 5\":\"rgb(165,0,38)\"}}}",
    "description" : "",
    "version" : 1,
    "kibanaSavedObjectMeta" : {
        "searchSourceJSON" : "{\"index\":\""+sid+"\",\"query\":{\"match_all\":{}},\"filter\":[]}"
    }
}
es.index(index='.kibana', doc_type='visualization', body=vis, id=vis_id)


# generate the time lion json object for the visualisation
def generateTimeLionQuerysCumulative():
    result=""
    for negative_field in field_map['negative']:
        result = result + ".es(q='"+negative_field+":4').color('red').label('"+negative_field+" cumulated').cusum(), "
    for positive_field in field_map['positive']:
        result = result + ".es(q='"+positive_field+":4').color('blue').label('"+positive_field+" cumulated').cusum(), "
    result = result[:-2] + ".legend(false)
    return result

def generateTimelionJSONObjectCumulative():
    jsonObject = {
        "title": "Reasons over time",
        "visState": "{\"type\": \"timelionCumulative\", \"title\": \"Reasons over time\", \"params\":{\"expression\":\""+generateTimeLionQuerysCumulative()+"\", \"interval\": \"1d\"}}"
    }
    return jsonObject

def generateTimeLionQueryBars():
    result=""
    for negative_field in field_map['negative']:
        result = result + ".es(q='"+negative_field+":4').color('red').label('"+negative_field+"').bars(), "
    for positive_field in field_map['positive']:
        result = result + ".es(q='"+positive_field+":4').color('blue').label('"+positive_field+"').bars(), "
    result = result[:-2] + ".legend(ne, 3)"
    return result

def generateTimelionJSONObjectBars():
    jsonObject = {
        "title": "Reasons over time",
        "visState": "{\"type\": \"timelionBars\", \"title\": \"Reasons over time\", \"params\":{\"expression\":\""+generateTimeLionQueryBars()+"\", \"interval\": \"1d\"}}"
    }
    return jsonObject

es.index(index='.kibana', doc_type='visualization', body=generateTimelionJSONObject(), id="timelionID")

# The next step is to create a dashboard with the gauge.
dashboard_id = 'dashythedashboard'
dashboard_json = {
    "title" : "Automatically generated dashboard",
    "hits" : 0,
    "description" : "This dashboard has been code-generated",
    "panelsJSON" : "[{\"size_x\":6,\"size_y\":6,\"panelIndex\":1,\"type\":\"visualization\",\"id\":\"timelionID\",\"col\":3,\"row\":1}]",
    "optionsJSON" : "{\"darkTheme\":false}",
    "uiStateJSON" : "{\"P-1\":{\"vis\":{\"defaultColors\":{\"0 - 1\":\"rgb(0,104,55)\",\"1 - 3\":\"rgb(255,255,190)\",\"3 - 5\":\"rgb(165,0,38)\"}}}}",
    "version" : 1,
    "timeRestore" : False,
    "kibanaSavedObjectMeta" : {
        "searchSourceJSON" : "{}"
    }
}
es.index(index='.kibana', doc_type='dashboard', body=dashboard_json, id=dashboard_id)



