import os
from azure.eventhub import EventHubConsumerClient
CONNECTION_STR = os.environ["EVENTHUB_CONN_STR"]
EVENTHUB_NAME = "orders"
def on_event(partition_context, event):
    data = event.body_as_json()
    print(f"partition={partition_context.partition_id} "
        f"seq={event.sequence_number} -> {data}")
client = EventHubConsumerClient.from_connection_string(
    CONNECTION_STR,
    consumer_group="$Default",
   eventhub_name=EVENTHUB_NAME,
)
print("Listening... press Ctrl+C to stop")
with client:
    client.receive(on_event=on_event, starting_position="-1") # -1 = from the beginning