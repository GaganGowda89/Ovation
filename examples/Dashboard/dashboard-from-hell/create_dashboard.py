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
sentiment_score_id = 'sentiment_score_' + tit
sentiment_score_title = 'Sentiment Score'
sentiment_score_field = field_map['summary'][0] # there is only one

vis =  {
    "title" : sentiment_score_title,
    "visState" : "{\"title\":\""+sentiment_score_title+"\",\"type\":\"pie\",\"params\":{\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"right\",\"isDonut\":false},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"split\",\"params\":{\"field\":\""+sentiment_score_field+"\",\"size\":5,\"order\":\"desc\",\"orderBy\":\"1\",\"row\":true}}],\"listeners\":{}}",
    "uiStateJSON" : "{}",
    "description" : "",
    "version" : 1,
    "kibanaSavedObjectMeta" : {
        "searchSourceJSON" : "{\"index\":\""+sid+"\",\"query\":{\"match_all\":{}},\"filter\":[]}"
    }
}   
es.index(index='.kibana', doc_type='visualization', body=vis, id=sentiment_score_id)


overall2_id = 'overall2_' + tit
overall2_title = 'Overall View'
overall2_field = field_map['summary'][0] # there is only one

vis = {
    "title" : overall2_title,
    "visState" : "{\"aggs\":[{\"enabled\":true,\"id\":\"1\",\"params\":{},\"schema\":\"metric\",\"type\":\"count\"},{\"enabled\":true,\"id\":\"2\",\"params\":{\"extended_bounds\":{},\"field\":\""+overall2_field+"\",\"interval\":1},\"schema\":\"segment\",\"type\":\"histogram\"}],\"listeners\":{},\"params\":{\"addLegend\":true,\"addTimeMarker\":false,\"addTooltip\":true,\"categoryAxes\":[{\"id\":\"CategoryAxis-1\",\"labels\":{\"show\":true,\"truncate\":100},\"position\":\"bottom\",\"scale\":{\"type\":\"linear\"},\"show\":true,\"style\":{},\"title\":{\"text\":\""+overall2_title+"\"},\"type\":\"category\"}],\"grid\":{\"categoryLines\":false,\"style\":{\"color\":\"#eee\"}},\"legendPosition\":\"right\",\"orderBucketsBySum\":true,\"seriesParams\":[{\"data\":{\"id\":\"1\",\"label\":\"Count\"},\"drawLinesBetweenPoints\":true,\"lineWidth\":5,\"mode\":\"stacked\",\"show\":\"true\",\"showCircles\":true,\"type\":\"histogram\",\"valueAxis\":\"ValueAxis-1\"}],\"times\":[],\"valueAxes\":[{\"id\":\"ValueAxis-1\",\"labels\":{\"filter\":false,\"rotate\":0,\"show\":true,\"truncate\":100},\"name\":\"LeftAxis-1\",\"position\":\"left\",\"scale\":{\"mode\":\"normal\",\"type\":\"linear\"},\"show\":true,\"style\":{},\"title\":{\"text\":\"Count\"},\"type\":\"value\"}]},\"title\":\"Overall_2\",\"type\":\"histogram\"}",
    "uiStateJSON" : "{\"vis\":{\"colors\":{\"Count\":\"#B7DBAB\"}}}",
    "description" : "",
    "version" : 1,
    "kibanaSavedObjectMeta" : {
        "searchSourceJSON" : "{\"index\":\""+sid+"\",\"query\":{\"match_all\":{}},\"filter\":[]}"
    }
}
es.index(index='.kibana', doc_type='visualization', body=vis, id=overall2_id)

sent_gauge_id = 'sentimentgauge_' + tit
sent_gauge_title = 'Sentiment Gauge'
sent_gauge_field = field_map['summary'][0] # there is only one

vis = {
    "title" : "Sentiment Gauge",
    "visState" : "{\"title\":\"Sentiment Gauge\",\"type\":\"gauge\",\"params\":{\"addTooltip\":true,\"addLegend\":true,\"gauge\":{\"verticalSplit\":false,\"extendRange\":true,\"percentageMode\":false,\"gaugeType\":\"Arc\",\"gaugeStyle\":\"Full\",\"backStyle\":\"Full\",\"orientation\":\"vertical\",\"colorSchema\":\"Green to Red\",\"gaugeColorMode\":\"Labels\",\"colorsRange\":[{\"from\":0,\"to\":2},{\"from\":2,\"to\":3},{\"from\":3,\"to\":5}],\"invertColors\":true,\"labels\":{\"show\":true,\"color\":\"black\"},\"scale\":{\"show\":true,\"labels\":false,\"color\":\"#333\"},\"type\":\"meter\",\"style\":{\"bgWidth\":0.9,\"width\":0.9,\"mask\":false,\"bgMask\":false,\"maskBars\":50,\"bgFill\":\"#eee\",\"bgColor\":false,\"subText\":\"\",\"fontSize\":60,\"labelColor\":true}}},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"avg\",\"schema\":\"metric\",\"params\":{\"field\":\""+sent_gauge_field+"\",\"customLabel\":\"Avg\"}}],\"listeners\":{}}",
    "uiStateJSON" : "{\"vis\":{\"colors\":{\"2 - 3\":\"#F9BA8F\"},\"defaultColors\":{\"0 - 2\":\"rgb(165,0,38)\",\"2 - 3\":\"rgb(255,255,190)\",\"3 - 5\":\"rgb(0,104,55)\"}}}",
    "description" : "",
    "version" : 1,
    "kibanaSavedObjectMeta" : {
        "searchSourceJSON" : "{\"index\":\""+sid+"\",\"query\":{\"match_all\":{}},\"filter\":[]}"
    }
}
es.index(index='.kibana', doc_type='visualization', body=vis, id=sent_gauge_id)


###################################
colors = ['red', 'green', 'rebeccapurple', 'darkmagenta', 'yellow', 'blue', 'deeppink', 'darkgreen', 'orange', 'darkgoldenrod', 'fuchsia', 'chocolate', 'coral', 'darkorchid', 'gold', 'MediumAquaMarin', 'Teal']

# generate the time lion json object for the visualisation
def generateTimeLionQuerysCumulative():
    result=""
    counter = 0
    for negative_field in field_map['negative']:
        result = result + ".es(index="+tit+", q='"+negative_field+":4').color('"+colors[counter]+"').label('"+negative_field+" cumulated').cusum(), "
        counter = counter + 1
    for positive_field in field_map['positive']:
        result = result + ".es(index="+tit+", q='"+positive_field+":4').color('"+colors[counter]+"').label('"+positive_field+" cumulated').cusum(), "
        counter = counter + 1
    result = result[:-2] + ".legend(false)"
    return result

def generateTimelionJSONObjectCumulative():
    jsonObject = {
        "title": "Trends",
        "visState": "{\"type\": \"timelion\", \"title\": \"Trends\", \"params\":{\"expression\":\""+generateTimeLionQuerysCumulative()+"\", \"interval\": \"1d\"}}"
    }
    return jsonObject

cumulated_id = 'All_reasons_real_good_colors_cumulated_' + tit
es.index(index='.kibana', doc_type='visualization', body=generateTimelionJSONObjectCumulative(), id=cumulated_id)

def generateTimeLionQueryBars():
    result=""
    counter = 1
    for negative_field in field_map['negative']:
        result = result + ".es(index="+tit+", q='"+negative_field+":4').color('"+colors[counter]+"').label('"+negative_field+"').bars(), "
        counter = counter + 1
    for positive_field in field_map['positive']:
        result = result + ".es(index="+tit+", q='"+positive_field+":4').color('"+colors[counter]+"').label('"+positive_field+"').bars(), "
        counter = counter + 1
    result = result[:-2] + ".legend(ne, 3)"
    return result

def generateTimelionJSONObjectBars():
    jsonObject = {
        "title": "Reasons",
        "visState": "{\"type\": \"timelion\", \"title\": \"Reasons\", \"params\":{\"expression\":\""+generateTimeLionQueryBars()+"\", \"interval\": \"1d\"}}"
    }
    return jsonObject

good_colors_id='good_colors_happy_colors_' + tit
es.index(index='.kibana', doc_type='visualization', body=generateTimelionJSONObjectBars(), id=good_colors_id)











geomap_id = 'geomapfoo_' + tit
geomap_title = 'GeoMap Sentiment'
geomap_src_loc = field_map['geography'][0] # there is only one
geomap_src_sum = field_map['summary'][0] # there is only one

vis = {
    "title" : geomap_title,
    "visState" : "{\"title\":\""+geomap_title+"\",\"type\":\"tile_map\",\"params\":{\"mapType\":\"Scaled Circle Markers\",\"isDesaturated\":true,\"addTooltip\":true,\"heatMaxZoom\":0,\"heatMinOpacity\":0.1,\"heatRadius\":25,\"heatBlur\":15,\"legendPosition\":\"topright\",\"mapZoom\":2,\"mapCenter\":[0,0],\"wms\":{\"enabled\":false,\"url\":\"https://basemap.nationalmap.gov/arcgis/services/USGSTopo/MapServer/WMSServer\",\"options\":{\"version\":\"1.3.0\",\"layers\":\"0\",\"format\":\"image/png\",\"transparent\":true,\"attribution\":\"Maps provided by USGS\",\"styles\":\"\"}}},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"top_hits\",\"schema\":\"metric\",\"params\":{\"field\":\""+geomap_src_sum+"\",\"aggregate\":\"average\",\"size\":1,\"sortField\":\""+geomap_src_sum+"\",\"sortOrder\":\"desc\"}},{\"id\":\"2\",\"enabled\":true,\"type\":\"geohash_grid\",\"schema\":\"segment\",\"params\":{\"field\":\""+geomap_src_loc+"\",\"autoPrecision\":true,\"useGeocentroid\":true,\"precision\":2}}],\"listeners\":{}}",
    "uiStateJSON" : "{\"mapZoom\":6,\"mapCenter\":[52.520008,13.404954]}",
    "description" : "",
    "version" : 1,
    "kibanaSavedObjectMeta" : {
        "searchSourceJSON" : "{\"index\":\""+sid+"\",\"query\":{\"match_all\":{}},\"filter\":[]}"
    }
}
es.index(index='.kibana', doc_type='visualization', body=vis, id=geomap_id)

src_cnt_id = 'sourcecntfoo_' + tit
src_cnt_title = 'Top two sources'
src_cnt_src = field_map['source'][0] # there is only one

vis =  {
    "title" : src_cnt_title,
    "visState" : "{\"title\":\""+src_cnt_title+"\",\"type\":\"metric\",\"params\":{\"addTooltip\":true,\"addLegend\":false,\"type\":\"gauge\",\"gauge\":{\"verticalSplit\":true,\"autoExtend\":false,\"percentageMode\":false,\"gaugeType\":\"Circle\",\"gaugeStyle\":\"Full\",\"backStyle\":\"Full\",\"orientation\":\"vertical\",\"colorSchema\":\"Green to Red\",\"gaugeColorMode\":\"None\",\"useRange\":false,\"colorsRange\":[{\"from\":0,\"to\":5000}],\"invertColors\":false,\"labels\":{\"show\":true,\"color\":\"black\"},\"scale\":{\"show\":false,\"labels\":false,\"color\":\"#333\",\"width\":2},\"type\":\"meter\",\"style\":{\"fontSize\":60,\"bgColor\":false,\"labelColor\":false,\"subText\":\"\"},\"minAngle\":0,\"maxAngle\":6.283185307179586}},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"group\",\"params\":{\"field\":\""+src_cnt_src+".keyword\",\"size\":2,\"order\":\"desc\",\"orderBy\":\"1\",\"customLabel\":\"Sources with the most feedback\"}}],\"listeners\":{}}",
    "uiStateJSON" : "{\"vis\":{\"defaultColors\":{\"0 - 100\":\"rgb(0,104,55)\"},\"legendOpen\":true,\"colors\":{\"0 - 100\":\"#962D82\"}}}",
    "description" : "",
    "version" : 1,
    "kibanaSavedObjectMeta" : {
        "searchSourceJSON" : "{\"index\":\""+sid+"\",\"query\":{\"match_all\":{}},\"filter\":[]}"
    }
}
es.index(index='.kibana', doc_type='visualization', body=vis, id=src_cnt_id)

src_graph_id = 'sourcegraphfoo_' + tit
src_graph_title = 'Sources'
src_graph_src = field_map['source'][0] # there is only one

vis = {
    "visState" : "{\"title\":\""+title+"\",\"type\":\"histogram\",\"params\":{\"grid\":{\"categoryLines\":false,\"style\":{\"color\":\"#eee\"}},\"categoryAxes\":[{\"id\":\"CategoryAxis-1\",\"type\":\"category\",\"position\":\"left\",\"show\":true,\"style\":{},\"scale\":{\"type\":\"linear\"},\"labels\":{\"show\":true,\"rotate\":0,\"filter\":false,\"truncate\":200},\"title\":{\"text\":\"Source\"}}],\"valueAxes\":[{\"id\":\"ValueAxis-1\",\"name\":\"LeftAxis-1\",\"type\":\"value\",\"position\":\"bottom\",\"show\":true,\"style\":{},\"scale\":{\"type\":\"linear\",\"mode\":\"normal\"},\"labels\":{\"show\":true,\"rotate\":75,\"filter\":true,\"truncate\":100},\"title\":{\"text\":\"Count\"}}],\"seriesParams\":[{\"show\":true,\"type\":\"histogram\",\"mode\":\"normal\",\"data\":{\"label\":\"Count\",\"id\":\"1\"},\"valueAxis\":\"ValueAxis-1\",\"drawLinesBetweenPoints\":true,\"showCircles\":true}],\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"right\",\"times\":[],\"addTimeMarker\":false},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"segment\",\"params\":{\"field\":\""+src_graph_src+".keyword\",\"size\":5,\"order\":\"desc\",\"orderBy\":\"1\",\"customLabel\":\"Source\"}}],\"listeners\":{}}",
    "description" : "",
    "title" : ""+src_graph_title+"",
    "uiStateJSON" : "{\"vis\":{\"colors\":{\"Count\":\"#BA43A9\"}}}",
    "version" : 1,
    "kibanaSavedObjectMeta" : {
        "searchSourceJSON" : "{\"index\":\""+sid+"\",\"query\":{\"match_all\":{}},\"filter\":[]}"
    }
}
es.index(index='.kibana', doc_type='visualization', body=vis, id=src_graph_id)


age_chart_id = 'age_graph_' + tit
age_chart_title = 'Age distribution'
age_chart_field = field_map['reviewer_age'][0] # there is only one

vis = {
    "title" : age_chart_title,
    "visState" : "{\"title\":\""+age_chart_title+"\",\"type\":\"histogram\",\"params\":{\"grid\":{\"categoryLines\":false,\"style\":{\"color\":\"#eee\"}},\"categoryAxes\":[{\"id\":\"CategoryAxis-1\",\"type\":\"category\",\"position\":\"bottom\",\"show\":true,\"style\":{},\"scale\":{\"type\":\"linear\"},\"labels\":{\"show\":true,\"truncate\":100},\"title\":{\"text\":\"age\"}}],\"valueAxes\":[{\"id\":\"ValueAxis-1\",\"name\":\"LeftAxis-1\",\"type\":\"value\",\"position\":\"left\",\"show\":true,\"style\":{},\"scale\":{\"type\":\"linear\",\"mode\":\"normal\"},\"labels\":{\"show\":true,\"rotate\":0,\"filter\":false,\"truncate\":100},\"title\":{\"text\":\"Count\"}}],\"seriesParams\":[{\"show\":\"true\",\"type\":\"histogram\",\"mode\":\"stacked\",\"data\":{\"label\":\"Count\",\"id\":\"1\"},\"valueAxis\":\"ValueAxis-1\",\"drawLinesBetweenPoints\":true,\"showCircles\":true}],\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"right\",\"times\":[],\"addTimeMarker\":false},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"histogram\",\"schema\":\"segment\",\"params\":{\"field\":\""+age_chart_field+"\",\"interval\":20,\"extended_bounds\":{}}}],\"listeners\":{}}",
    "uiStateJSON" : "{}",
    "description" : "",
    "version" : 1,
    "kibanaSavedObjectMeta" : {
        "searchSourceJSON" : "{\"index\":\""+sid+"\",\"query\":{\"match_all\":{}},\"filter\":[]}"
    }
}
es.index(index='.kibana', doc_type='visualization', body=vis, id=age_chart_id)


agepie_id = 'agepie_' + tit
agepie_title = 'Age distribution'
agepie_field = field_map['reviewer_age'][0] # there is only one

vis = {
    "title" : agepie_title,
    "visState" : "{\"title\":\""+agepie_title+"\",\"type\":\"pie\",\"params\":{\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"right\",\"isDonut\":false},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"range\",\"schema\":\"split\",\"params\":{\"field\":\""+agepie_field+"\",\"ranges\":[{\"from\":0,\"to\":20},{\"from\":20,\"to\":40},{\"from\":40,\"to\":60},{\"from\":60,\"to\":80},{\"from\":80,\"to\":100}],\"row\":true}}],\"listeners\":{}}",
    "uiStateJSON" : "{}",
    "description" : "",
    "version" : 1,
    "kibanaSavedObjectMeta" : {
        "searchSourceJSON" : "{\"index\":\""+sid+"\",\"query\":{\"match_all\":{}},\"filter\":[]}"
    }
}
es.index(index='.kibana', doc_type='visualization', body=vis, id=agepie_id)





def generateGenderPieChart():
    jsonObject = {
        "title":"Gender distribution",
        "visState": "{\"title\": \"Gender distribution\", \"type\": \"pie\", \"params\": {\"addTooltip\": true, \"addLegend\": true, \"legendPosition\": \"right\", \"isDonut\": false}, \"aggs\": [{\"id\": \"1\", \"enabled\": true, \"type\": \"count\", \"schema\": \"metric\", \"params\":{}}, {\"id\":\"2\", \"enabled\":true, \"type\":\"terms\", \"schema\":\"split\", \"params\":{\"field\":\""+field_map['reviewer_gender'][0]+".keyword\", \"size\":\"5\", \"order\":\"desc\", \"orderBy\":\"1\", \"row\":true}}], \"listeners\":{}}",
        "uiStateJSON": "{}",
        "description": "",
        "version": "1",
        "kibanaSavedObjectMeta": {
            "searchSourceJSON": "{\"index\":\""+sid+"\", \"query\":{\"match_all\":{}}, \"filter\":[]}"
        }
    }
    return jsonObject
genderpie_id='gender_pie_' + tit
es.index(index='.kibana', doc_type='visualization', body=generateGenderPieChart(), id=genderpie_id)




vis_id = 'source_bar_graph_' + tit
vis_title = 'My gauge'
vis_source_field = field_map['reviewer_gender'][0] # there is only one
vis = {
      "title": "Gender distribution",
      "visState": "{\"title\":\"Gender distribution\",\"type\":\"histogram\",\"params\":{\"grid\":{\"categoryLines\":false,\"style\":{\"color\":\"#eee\"}},\"categoryAxes\":[{\"id\":\"CategoryAxis-1\",\"type\":\"category\",\"position\":\"left\",\"show\":true,\"style\":{},\"scale\":{\"type\":\"linear\"},\"labels\":{\"show\":true,\"rotate\":0,\"filter\":false,\"truncate\":200},\"title\":{\"text\":\"Gender\"}}],\"valueAxes\":[{\"id\":\"ValueAxis-1\",\"name\":\"LeftAxis-1\",\"type\":\"value\",\"position\":\"bottom\",\"show\":true,\"style\":{},\"scale\":{\"type\":\"linear\",\"mode\":\"normal\"},\"labels\":{\"show\":true,\"rotate\":75,\"filter\":true,\"truncate\":100},\"title\":{\"text\":\"Count\"}}],\"seriesParams\":[{\"show\":true,\"type\":\"histogram\",\"mode\":\"normal\",\"data\":{\"label\":\"Count\",\"id\":\"1\"},\"valueAxis\":\"ValueAxis-1\",\"drawLinesBetweenPoints\":true,\"showCircles\":true}],\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"right\",\"times\":[],\"addTimeMarker\":false},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"segment\",\"params\":{\"field\":\""+vis_source_field+".keyword\",\"size\":100,\"order\":\"desc\",\"orderBy\":\"1\",\"customLabel\":\"Gender\"}}],\"listeners\":{}}",
      "uiStateJSON": "{}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\""+sid+"\",\"query\":{\"match_all\":{}},\"filter\":[]}"
      }
    }
es.index(index='.kibana', doc_type='visualization', body=vis, id=vis_id)


# Creating the filters
filters = "{\"filter\":[{\"query\":{\"match_all\":{}}}],\"highlightAll\":true,\"version\":true}"
if len(field_map['filter'])>0:
    filters = "{\"filter\":["
    first = True
    for fn in field_map['filter']:
        r = requests.get(host+'/'+tit+'/_search?q='+fn+':*&size=100')
        j = r.json();
        values = set()
        for record in j['hits']['hits']:
            values.add(record['_source'][fn])
        print(values)
        for name in values:
            if first == False:
                filters = filters + ','
            filters = filters + "{\"meta\":{\"index\":\""+sid+"\",\"negate\":false,\"disabled\":true,\"alias\":null,\"type\":\"phrase\",\"key\":\""+fn+"\",\"value\":\""+name+"\"},\"query\":{\"match\":{\""+fn+"\":{\"query\":\""+name+"\",\"type\":\"phrase\"}}},\"$state\":{\"store\":\"appState\"}}"
            first = False
    filters = filters + "],\"highlightAll\":true,\"version\":true}"

# The next step is to create a dashboard with the gauge.
dashboard_id = 'dashythedashboard_'+tit
dashboard_json = {
    "title": "zee",
    "hits": 0,
    "description": "Dashboard for "+tit,
    "panelsJSON": "[{\"col\":1,\"id\":\""+sentiment_score_id+"\",\"panelIndex\":2,\"row\":1,\"size_x\":4,\"size_y\":3,\"type\":\"visualization\"},{\"col\":5,\"id\":\""+overall2_id+"\",\"panelIndex\":11,\"row\":1,\"size_x\":4,\"size_y\":3,\"type\":\"visualization\"},{\"col\":9,\"id\":\""+sent_gauge_id+"\",\"panelIndex\":22,\"row\":1,\"size_x\":4,\"size_y\":3,\"type\":\"visualization\"},{\"col\":4,\"id\":\""+cumulated_id+"\",\"panelIndex\":19,\"row\":4,\"size_x\":3,\"size_y\":3,\"type\":\"visualization\"},{\"col\":1,\"id\":\""+good_colors_id+"\",\"panelIndex\":20,\"row\":4,\"size_x\":3,\"size_y\":3,\"type\":\"visualization\"},{\"col\":7,\"id\":\""+geomap_id+"\",\"panelIndex\":3,\"row\":4,\"size_x\":6,\"size_y\":3,\"type\":\"visualization\"},{\"col\":1,\"id\":\""+src_cnt_id+"\",\"panelIndex\":16,\"row\":7,\"size_x\":3,\"size_y\":4,\"type\":\"visualization\"},{\"col\":4,\"id\":\""+src_graph_id+"\",\"panelIndex\":15,\"row\":7,\"size_x\":3,\"size_y\":4,\"type\":\"visualization\"},{\"col\":7,\"id\":\""+age_chart_id+"\",\"panelIndex\":12,\"row\":9,\"size_x\":3,\"size_y\":2,\"type\":\"visualization\"},{\"col\":7,\"id\":\""+agepie_id+"\",\"panelIndex\":9,\"row\":7,\"size_x\":3,\"size_y\":2,\"type\":\"visualization\"},{\"col\":10,\"id\":\""+genderpie_id+"\",\"panelIndex\":10,\"row\":7,\"size_x\":3,\"size_y\":2,\"type\":\"visualization\"},{\"col\":10,\"id\":\""+vis_id+"\",\"panelIndex\":23,\"row\":9,\"size_x\":3,\"size_y\":2,\"type\":\"visualization\"}]",
    "optionsJSON": "{\"darkTheme\":false}",
    "uiStateJSON": "{}",
    "version": 1,
    "timeRestore": false,
    "kibanaSavedObjectMeta": {
        #"searchSourceJSON": "{\"filter\":[{\"query\":{\"match_all\":{}}}],\"highlightAll\":true,\"version\":true}"
        "searchSourceJSON" : filters
    }
}
es.index(index='.kibana', doc_type='dashboard', body=dashboard_json, id=dashboard_id)


