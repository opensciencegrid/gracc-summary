import toml
import argparse
import pika


class SummaryAgent(object):
    
    def __init__(self, config):
        with open(config) as conffile:
            self._config = toml.loads(conffile.read())
        
    def run(self):
        
        # Setup AMQP to listen for summary records
        # AMQP Event Loop
        self.amqpConnect()
        self._chan.basic_consume(self._receiveMsg, self._config['AMQP']['listen_queue'])
        
        try:
            self._chan.start_consuming()
        except KeyboardInterrupt:
            self._chan.stop_consuming()
        
        
    def amqpConnect(self):
        credentials = pika.PlainCredentials(self._config['AMQP']['username'], self._config['AMQP']['password'])
        self.parameters = pika.ConnectionParameters(self._config['AMQP']['host'],
                                                5672, self._config['AMQP']['vhost'], credentials)
        self._conn = pika.adapters.blocking_connection.BlockingConnection(self.parameters)
        
        self._chan = self._conn.channel()
        # Create the exchange, if it doesn't already exist
        # TODO: capture exit codes on all these call
        self._chan.exchange_declare(exchange=self._config['AMQP']['listen_exchange'], exchange_type='direct')
        self._chan.queue_declare(queue=self._config['AMQP']['listen_queue'])
        self._chan.queue_bind(self._config['AMQP']['listen_queue'], self._config['AMQP']['listen_exchange'])



def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="GRACC Summary Agent")
    parser.add_argument("-c", "--configuration", help="Configuration file location",
                        default="/etc/graccsum/config.toml", dest='config')
    args = parser.parse_args()
    
    
    # Create and run the OverMind
    summary_agent = SummaryAgent(args.config)
    summary_agent.run()
