import argparse

from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONDeserializer


API_KEY = 'X6NPTES7QB5CBBVF'
ENDPOINT_SCHEMA_URL  = 'https://psrc-l622j.us-east-2.aws.confluent.cloud'
API_SECRET_KEY = 'YFZREeAkUSzwC785QlxTy9oM1x5MYdO3r4jDoYVg4uNv3uoHRB9p15KVwOtUbxp3'
BOOTSTRAP_SERVER = 'pkc-921jm.us-east-2.aws.confluent.cloud:9092'
SECURITY_PROTOCOL = 'SASL_SSL'
SSL_MACHENISM = 'PLAIN'
SCHEMA_REGISTRY_API_KEY = 'EHBI7LOTYWMEJGK7'
SCHEMA_REGISTRY_API_SECRET = '2u2XAJkOc2F8cMbsBYqpovHn9Hat4J9hk4PZG26PIFN0PRB/V+V8G5AUA/9YE2Qy'

def sasl_conf():

    sasl_conf = {'sasl.mechanism': SSL_MACHENISM,
                 # Set to SASL_SSL to enable TLS support.
                #  'security.protocol': 'SASL_PLAINTEXT'}
                'bootstrap.servers':BOOTSTRAP_SERVER,
                'security.protocol': SECURITY_PROTOCOL,
                'sasl.username': API_KEY,
                'sasl.password': API_SECRET_KEY
                }
    return sasl_conf



def schema_config():
    return {'url':ENDPOINT_SCHEMA_URL,
    
    'basic.auth.user.info':f"{SCHEMA_REGISTRY_API_KEY}:{SCHEMA_REGISTRY_API_SECRET}"

    }


class Order:   
    def __init__(self,record:dict):
        for k,v in record.items():
            setattr(self,k,v)
        
        self.record=record
   
    @staticmethod
    def dict_to_order(data:dict,ctx):
        return Order(record=data)

    def __str__(self):
        return f"{self.record}"


def main(topic):

    schema_str = """
    {
  "$id": "http://example.com/myURI.schema.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "additionalProperties": false,
  "description": "Sample schema to help you get started.",
  "properties": {
    "Order Number": {
      "description": "The type(v) type is used.",
      "type": "number"
    },
    "Order Date": {
      "description": "The type(v) type is used.",
      "type": "string"
    },
    "Item Name": {
      "description": "The type(v) type is used.",
      "type": "string"
    },
    "Quantity": {
      "description": "The type(v) type is used.",
      "type": "number"
    },
    "Product Price": {
      "description": "The type(v) type is used.",
      "type": "number"
    },
    "Total Products": {
      "description": "The type(v) type is used.",
      "type": "number"
    }
  },
  "title": "SampleRecord",
  "type": "object"
}
    """
    json_deserializer = JSONDeserializer(schema_str,
                                         from_dict=Order.dict_to_order)

    consumer_conf = sasl_conf()
    consumer_conf.update({
                     'group.id': 'group1',
                     'auto.offset.reset': "latest"})

    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])


    while True:
        try:
            # SIGINT can't be handled when polling, limit timeout to 1 second.
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            order = json_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))

            if order is not None:
                print("User record {}: order: {}\n"
                      .format(msg.key(), order))
        except KeyboardInterrupt:
            break

    consumer.close()

main("restaurent-take-away-data")
