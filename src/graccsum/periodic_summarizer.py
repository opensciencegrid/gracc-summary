import toml
import argparse
from datetime import datetime, timedelta
from graccreq import Client


class PeriodicSummarizer(object):
    
    def __init__(self, config):
        
        self._config = config
        
    def runRules(self):
        
        while True:
            # Every 15 minutes, resummarize the last 7 days
            client = Client("gracc.osg.requests", "gracc.osg.requests")
            
            # Get today's date, and the date 7 days ago
            end_time = datetime.today()
            start_time = end_time - timedelta(days=7)
            
            client.query(start_time, end_time, 'summary', 
                destination_exchange=self._config['PeriodicSummarizer']['destination_exchange'], 
                destination_key=self._config['PeriodicSummarizer']['destination_key'])
        
            # now sleep for 15 minutes...
            time.sleep(60*15)
        
        
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


