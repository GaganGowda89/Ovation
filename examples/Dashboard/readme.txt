Python requires the elasticsearch library. With Archlinux, the package
is called
    python-elasticsearch

To have a constant update of the visualizations:
    1) Management
    2) Advanced settings
    3) timepicker:refreshIntervalDefaults
    4) { "display": "Off", "pause": true, "value": 1000 }
You might nead to restart Kibana afterwards. In Archlinux, run as
root
    systemctl restart kibana

To have correct data types:
    1) In case of numbers, cast correctly row[] in the python script
    2) In case of dates, locations or types which are not detected
       correctly, add them to the mapping in python
    3) To update types in Kibana, remove and add again the index,
       otherwise you will still have the "old" type
Note that step 3) is required because Kibana keeps a copy of the
index structure in a separate index, i.e., it's storing redundant
data.

To work with requests in python, python-requests is needed.
