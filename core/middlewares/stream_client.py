import pika
from core.env import config
 
# Connect to RabbitMQ
credentials = pika.PlainCredentials(config.RABBIT_MQ_USER, config.RABBITMQ_DEFAULT_PASS)
parameters = pika.ConnectionParameters(config.RABBITMQ_HOSTNAME,
                                       config.RABBITMQ_PORT,
                                       'ashvdjpb',
                                       credentials)
connection = pika.BlockingConnection(parameters=parameters) # add container name in docker

class RabbitMQClient:
    def __init__(self):
        self.connection = connection
        self.channel = self.connection.channel()

        # Declare the queues
        self.channel.queue_declare(queue='A_to_B')
        self.channel.queue_declare(queue='B_to_A')

    def send_message(self, message: str):
        self.channel.basic_publish(exchange='',
                                   routing_key='A_to_B',
                                   body=message)
        print(f"Sent message to B: {message}")


    def start_consuming(self):
        def callback(ch, method, properties, body):
            print(f"Received message from B: {body.decode()}")

        self.channel.basic_consume(queue='B_to_A',
                                   on_message_callback=callback,
                                   auto_ack=True)

        print(" [*] Waiting for messages from B. To exit press CTRL+C")
        self.channel.start_consuming()

client = RabbitMQClient()
