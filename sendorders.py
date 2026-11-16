import json, os, random, uuid

from datetime import datetime, timezone

from azure.eventhub import EventHubProducerClient, EventData

CONNECTION_STR = os.environ["EVENTHUB_CONN_STR"]

EVENTHUB_NAME = "orders"

PRODUCTS = ["Laptop", "Monitor", "Keyboard", "Mouse"]

REGIONS = ["EAST", "WEST", "NORTH", "SOUTH"]

def make_order():

   return {

        "event_id": str(uuid.uuid4()),

       "customer_id": random.randint(100, 105),

       "product": random.choice(PRODUCTS),

        "quantity": random.randint(1, 5),

        "amount": round(random.uniform(20, 2000), 2),

        "region": random.choice(REGIONS),

        "event_ts": datetime.now(timezone.utc).isoformat(),

    }

producer = EventHubProducerClient.from_connection_string(

    CONNECTION_STR, eventhub_name=EVENTHUB_NAME

)

with producer:

    batch = producer.create_batch()

    for _ in range(100):

        event = EventData(json.dumps(make_order()))

        try:

            batch.add(event)

        except ValueError:              # batch is full: send it and start a new one

            producer.send_batch(batch)

            batch = producer.create_batch()

            batch.add(event)

    producer.send_batch(batch)          # send what's left

print("Sent 100 order events")
 