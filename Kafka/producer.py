from kafka import KafkaProducer
import json
import time
 
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)
 
for i in range(1, 11):

    order = {
        "order_id": i,
        "customer_id": f"C{i}",
        "amount": i * 100
    }
 
    partition = (i - 1) % 3 # distributing based on 3 paritions
 
    result = producer.send(
        "orders-python",
        value=order,
        partition=partition
    ).get(timeout=10)

    print(
        f"Order {i} -> "
        f"Partition {result.partition}, "
        f"Offset {result.offset}"
    )
 
    time.sleep(1)
producer.flush()
producer.close()
 