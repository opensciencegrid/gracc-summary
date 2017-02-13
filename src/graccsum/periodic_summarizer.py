import toml
import argparse
from datetime import datetime, timedelta
from graccreq import Client
import logging
import time


class PeriodicSummarizer(object):
    
    def __init__(self, config):
        
        with open(config) as conffile:
            self._config = toml.loads(conffile.read())
            
        logging.basicConfig(level=logging.DEBUG)
        
    def runRules(self, restrict_type = None):
        
        for summary_name in self._config['Summary']:
            cur_type = self._config['Summary'][summary_name]
            logging.debug("Starting the summary: %s" % summary_name)
            # Every 15 minutes, resummarize the last 7 days
            client = Client(
                exchange=self._config['PeriodicSummarizer']['request_exchange'],
                routing_key=self._config['PeriodicSummarizer']['request_key'],
                host=self._config['AMQP']['host'],
                vhost=self._config['AMQP']['vhost'],
                username=self._config['AMQP']['username'],
                password=self._config['AMQP']['password'])
            
            # Get today's date, and the date 7 days ago
            end_time = datetime.today()
            start_time = end_time - timedelta(days=7)
            
            logging.debug("Starting query to remote requster")
            client.query(start_time, end_time, cur_type['summary_type'], 
                destination_exchange=cur_type['destination_exchange'], 
                destination_key=cur_type['destination_key'])
        
        
        
    def run(self):
        """
        Begin the periodic summarizer duties
        
        """
        
        self.runRules()
    
    

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="GRACC Periodic Summary Agent")
    parser.add_argument("-c", "--configuration", help="Configuration file location",
                        default="/etc/graccsum/config.toml", dest='config')
    args = parser.parse_args()
    
    
    # Create and run the OverMind
    summary_agent = PeriodicSummarizer(args.config)
    summary_agent.run()


