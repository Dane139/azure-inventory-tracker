import sys
from azure.servicebus import ServiceBusClient, ServiceBusMessage

conn_str = sys.argv[1]

message_body = '{"sale_id":"TEST-001","product_id":1,"quantity":2}'

with ServiceBusClient.from_connection_string(conn_str) as client:
    with client.get_queue_sender("sale-events") as sender:
        sender.send_messages(ServiceBusMessage(message_body))
        print("Message sent successfully")
