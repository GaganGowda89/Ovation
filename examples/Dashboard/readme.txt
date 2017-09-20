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
