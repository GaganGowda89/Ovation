This example uses elasticsearch as its database, and kibana for the visualisation.
Make sure this are installed and running. We developed it with version 5.6 of elastic and kibana.

After you started elasticsearch, you can just start populate.py. 
It will create an index pattern and fills it with some data from the amazon_gt file.
After that, you can run create_dashboard. Just follow the instructions on it and it will create the dashboard automatically.
Then you can open kibana and look for the dashboard 'zee'.


Python requires the elasticsearch library. With Archlinux, the package
is called
    python-elasticsearch

To have a constant update of the visualizations:
    1) Management
    2) Advanced settings
    3) timepicker:refreshIntervalDefaults
    4) { "display": "On", "pause": true, "value": 1000 }
You might nead to restart Kibana afterwards. In Archlinux, run as
root
    systemctl restart kibana
After that, you can start the automatic updates by clicking on the little arrow in the top left of the screen

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

 
      
  # How to load the Elastic Search Instance to other client using Kibana
  
     1) Set the configuration setup in the sharing machine by changing the elasticsearch.yml
     
     ```sh
     # Change directory to the config where the elasticsearch.yml is located
     # environment
     cd /elasticsearch-5.6.1/config/elasticsearch.yml

      
     network.host: 0.0.0.0
     transport.host: localhost
     #
     # Set a custom port for HTTP:
     #
     http.port: 9200
     ```
     
     2) The client using the above elasticsearch instance could verify with the IP address of the sharing machine
     
     ```sh
     curl http://ipaddr:9200
     ```
     3) To access the dashboard of the Kibana from the other machine, setup the kibana.yml file with the IP address of the 
     shared machine
     
     ```sh
     # Change directory to the config where the elasticsearch.yml is located
     # environment
     cd /kibana-5.6.1/config/kibana.yml
     
     # The URL of the Elasticsearch instance to use for all your queries.
     elasticsearch.url: "http://ip-addr-of-shared-machine:9200"
     
     4) The shared Dashboard link should be working fine now...!!!
