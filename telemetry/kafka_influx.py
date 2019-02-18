#!/usr/bin/env python
import yaml
import json
from kafka import KafkaConsumer
import time
import requests
import time
import copy
from itertools import chain, islice

IP = "35.185.225.152"
# IP = "100.96.0.22"


def print_format_influxdb(d):
    """
    Print all datapoints to STDOUT in influxdb format for Telegraf to pick them up
    """
   
    print(format_datapoints_inlineprotocol(d))

def post_format_influxdb(d, addr="http://localhost:8186/write"):

    resp = requests.post(addr, data=format_datapoints_inlineprotocol(d))

    print('Sent Datapoint to: %s %s' % (addr, resp.status_code))


def format_datapoints_inlineprotocol(datapoint):
    """
    Format all datapoints with the inlineprotocol (influxdb)
    """

    ## Format Tags
    if not datapoint:
        return ""

    tags = ''
    first_tag = 1
    if datapoint['tags']:
        for tag, value in datapoint['tags'].items():

            if first_tag == 1:
                first_tag = 0
            else:
                tags = tags + ','

            tags = tags + '{0}={1}'.format(tag,value)

    ## Format Measurement
    fields = ''
    first_field = 1
    for tag, value in datapoint['fields'].items():

        if first_field == 1:
            first_field = 0
        else:
            fields = fields + ','

        fields = fields + '{0}={1}'.format(tag,value)

    if datapoint['tags']:
        formatted_data = "{0},{1} {2}".format(datapoint['measurement'], tags, fields)
    else:
        formatted_data = "{0} {1}".format(datapoint['measurement'], fields)

    return formatted_data


DATAPOINT_TPL = {
        "tags": {
        },
        "fields": {
        },
        "measurement":None,
        'timestamp': None
    }

class Consumer():
    def run(self):
        consumer = KafkaConsumer(bootstrap_servers=IP+':9092',
                                 auto_offset_reset='largest', 
                                 enable_auto_commit=True)
        consumer.subscribe(['device_rtr1', 'device_rtr3', 'device_rtr2','device_rtr4' ])
        

        for message in consumer:

            # print(message)
            inputdata = json.loads(message.value.decode('unicode_escape').strip('"')) # .decode('string-escape'))

            if not isinstance(inputdata, dict):
                print(inputdata)
                print("inputdata is of type %s" %  type(inputdata))
                continue

            if 'update' not in inputdata["update"]:
                continue
                
            for data in inputdata["update"]["update"]:

                if 'path' in data.keys() and 'elem' in data['path'].keys():
                    
                    if data['path']['elem'][2]['name'] != "counters": 
                        continue    

                    datapoint = copy.deepcopy(DATAPOINT_TPL)

                    datapoint['timestamp'] = int(time.time())

                    ## Extract Data type
                    dtype = "{}_{}".format(
                        data['path']['elem'][0]['name'],
                        data['path']['elem'][3]['name']
                    )   

                    datapoint["measurement"] = dtype.replace('-', '_')

                    item = data['path']['elem'][0]['key']['name']

                    ## Extract Value
                    vkeys = list(data['val'].keys())

                    if vkeys[0] == "stringVal": 
                        continue 

                    value = data['val'][vkeys[0]]

                    datapoint['tags']['device'] = message.topic.split('_')[1]
                    datapoint['tags']['key'] = item
                    
                    datapoint['fields']['value'] = int(value)
                    
                    # print("{} {} {} {}".format(
                    #         message.topic,
                    #         dtype,
                    #         item,
                    #         value 
                    #     ))

                    print_format_influxdb(datapoint)
                    post_format_influxdb(datapoint)

                # print(json.loads(message.value))

def main():
    consumer =  Consumer()
    consumer.run()


if __name__ == "__main__":
    main()

