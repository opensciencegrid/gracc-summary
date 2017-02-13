import pika

credentials = pika.PlainCredentials("guest", "guest")
parameters = pika.ConnectionParameters("localhost",
                                                5672, "/", credentials)
conn = pika.adapters.blocking_connection.BlockingConnection(parameters)

channel = conn.channel()

channel.exchange_declare(exchange="gracc.osg.summary", exchange_type='fanout', durable=True, auto_delete=False)


channel.exchange_declare(exchange="gracc.osg.transfer-summary", exchange_type='fanout', durable=True, auto_delete=False)

