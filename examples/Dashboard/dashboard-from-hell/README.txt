Congratulations for opening a readme file. Problems to sleep at night?
Train/plane delayed? That's what readme files are for!

This amazing documentation is composed of the following parts:
1) installation of ElasticSearch,
2) installation and configuration of Kibana,
3) importation of data into the database
4) dashboard automatic generation

1) Installation of ElasticSearch
ElasticSearch (ES) is a mix between a search engine and a non-relational
database. If you use Linux you can probably get it from your repos.
Otherwise:
    https://www.elastic.co/en/products/elasticsearch
Note that ES can be distributed over several computers. If you want to
have remote access, you will have to open the port 9200.

2) Installation & Configuration of Kibana
In short, Kibana is a data visualization/exploration tool which is
built on top of ElasticSearch. You will need either to:
    a) install ES first, and then Kibana,
    b) install Kibana and configure it to use ES on a remote computer
Note the second option is pretty cool as you can have great graphics on
a weak computer.

For b), you will have to go throug hthe following steps:
    1) locate elasticsearch.yml
    2) set the network host using the following pattern:
        network.host: 0.0.0.0
    3) set the transport host:
        transport.host: localhost
    4) if needed, indicate which port has to be used:
        http.port: 9200
    5) update the ES search url:
        elasticsearch.url: "http://remote-host:9200"

3) Importation of Data
For this, as well as for 4), you will need to install the following
Python libraries:
    python-elasticsearch
    python-requests
Depending on your operating system, the package names might differ. Note
that we used Python 3.?, so if it does not work, make sure you are using
a recent version of Python.

To import data that can be used by our system, you will need to use as
template import-hotels.py or import-insurance.py. You can decide which
field names you want to provide, but you have then to add some metadata
indicating what they correspond to (types = {...):
    positive -> good thing
    negative -> bad thing
    reason -> criterion used by the reviewer
    number -> this is numeric data
    text -> this is text data
    timeline -> date of the review
    demography -> demographical data
    reviewer_age -> reviewer's age
    summary -> "the" sentiment measurement
    geography -> position on a map
    reviewer_gender -> what it means
    filter -> field with few different values that can be used as filter
    source -> raw message content
Run the importation script and an index will be created.

4) Dashboard creation
Import the index containing your data in Kibana. Then, run the python
dashboard creation. Select the indec and doc types for the data and the
metadata.
Enjoy !
