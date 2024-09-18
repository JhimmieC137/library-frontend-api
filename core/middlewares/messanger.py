import pika
import time
from core.env import config
from collections import deque
 
# Connect to RabbitMQ
credentials = pika.PlainCredentials(config.RABBIT_MQ_USER, config.RABBITMQ_DEFAULT_PASS)
parameters = pika.ConnectionParameters(config.RABBITMQ_HOSTNAME,
                                    config.RABBITMQ_PORT,
                                    'ashvdjpb',
                                    credentials,
                                    heartbeat=600)
connection = pika.BlockingConnection(parameters=parameters) # add container name in docker



class MessagingClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.unsent_messages = deque()  # Queue to hold unsent messages
        self.connect()

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(parameters=parameters)
            self.channel = self.connection.channel()

            # Declare the queues
            self.channel.queue_declare(queue='B_to_A')

            # Retry sending unsent messages
            self.retry_unsent_messages()
        except Exception as e:
            print(f"Connection error: {e}")
            time.sleep(5)  # Wait before retrying
            self.connect()  # Retry connection

    def send_message(self, message: str):
        if self.channel and self.connection.is_open:
            try:
                self.channel.basic_publish(
                    exchange='',
                    routing_key='B_to_A',
                    body=message
                )
                print(f"Sent message to B: {message}")
                
            except pika.exceptions.StreamLostError:
                print("Error sending message, connection lost.")
                self.unsent_messages.append(message)
                self.connect()  # Reconnect
            except pika.exceptions.ChannelWrongStateError:
                print("Channel in wrong state.")
            except Exception as e:
                print(f"Unexpected error: {e}")
        else:
            print("Channel is not open. Adding message to queue.")
            self.unsent_messages.append(message)
            self.connect()  # Reconnect

    def retry_unsent_messages(self):
        while self.unsent_messages:
            message = self.unsent_messages.popleft()
            self.send_message(message)

    def close(self):
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()

client = MessagingClient()