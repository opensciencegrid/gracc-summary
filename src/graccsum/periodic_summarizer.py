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
        
    def runRules(self, timeperiod, restrict_type = None):
        
        for summary_name in self._config['Summary']:
            cur_type = self._config['Summary'][summary_name]
            logging.debug("Starting the summary: %s" % summary_name)
            # Every 15 minutes, resummarize the last 7 days
            client = Client(
                exchange=self._config['PeriodicSummarizer']['request_exchange'],
                routing_key=self._config['PeriodicSummarizer']['request_key'],
                url=self._config['AMQP']['url'])
            
            # Get today's date, and the date 7 days ago
            end_time = datetime.today()
            start_time = end_time - timedelta(days=timeperiod)
            
            while (start_time < end_time):
                tmp_to_date = min(start_time + timedelta(days=7), end_time)
                print "Summarizing %s to %s" % (start_time.isoformat(), tmp_to_date.isoformat())
                client.query(start_time, tmp_to_date, cur_type['summary_type'], destination_exchange=cur_type['destination_exchange'], destination_key=cur_type['destination_key'])
                
                # Update the from date
                start_time = tmp_to_date
            
        
        
        
    def run(self, timeperiod):
        """
        Begin the periodic summarizer duties
        
        :param int timeperiod: The number of days to summarize in the past, ending on the current day.
        """
        
        self.runRules(timeperiod)
    
    

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="GRACC Periodic Summary Agent")
    parser.add_argument("-c", "--configuration", help="Configuration file location", default="/etc/graccsum/config.toml", dest='config')                
    parser.add_argument("-t", "--timeperiod", help="Time Period in days to summarize, ending on the current day", default="7", dest='timeperiod', type=int)
    args = parser.parse_args()
    
    
    # Create and run the OverMind
    summary_agent = PeriodicSummarizer(args.config)
    summary_agent.run(args.timeperiod)


