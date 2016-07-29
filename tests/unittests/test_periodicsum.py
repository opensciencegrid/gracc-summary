
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import unittest
import datetime
import dateutil.parser
import random
import pika
import json
import subprocess
import time



class TestPeriodicSummarizer(unittest.TestCase):
    
    def setUp(self):
        """
        Upload new data with updated EndTimes
        """
        
        ZERO = datetime.timedelta(0)

        class UTC(datetime.tzinfo):
          def utcoffset(self, dt):
            return ZERO
          def tzname(self, dt):
            return "UTC"
          def dst(self, dt):
            return ZERO

        utc = UTC()
        
        # Connect and query the elasticsearch database
        client = Elasticsearch()
        s = Search(using=client)
        s.query("match_all")
        response = s.execute()
        to_upload = []
        
        # Upload the new records to ElasticSearch
        credentials = pika.PlainCredentials("guest", "guest")
        parameters = pika.ConnectionParameters("localhost",
                                                5672, "/", credentials)
        self.conn = pika.adapters.blocking_connection.BlockingConnection(parameters)
        
        self.channel = self.conn.channel()
        
        # Update the EndTimes
        for hit in s.scan():
            print hit.EndTime
            # Determine the number of days between the current EndTime and now
            try:
                cur_endtime = dateutil.parser.parse(hit.EndTime)
                diff = datetime.datetime.now(utc) - cur_endtime
            except:
                # Sometimes the endtime is list
                print hit
                print "EndTime is list"
                continue
            print "Difference in days is %i" % diff.days
            # Randomly subtract between 0-6 days from the EndTime
            diff -= datetime.timedelta(days=random.randint(0,6))
            print "New difference in days is %i" % diff.days
            
            # Update the new EndTime and add to upload
            hit.EndTime = (cur_endtime + diff).isoformat()
            print "New EndTime = %s" % hit.EndTime
            self.channel.basic_publish("gracc.osg.summary",
                                  "gracc.osg.summary",
                                  json.dumps(hit.to_dict()),
                                  pika.BasicProperties(content_type='text/json',
                                                       delivery_mode=1))
            to_upload.append(hit) 
        
        

        
        pass
        
    def test_periodic_summarizer(self):
        
        # Restart the graccsumperiodic service 
        subprocess.call("systemctl restart graccsumperiodic.service", shell=True)
        
        # Wait for a bit to make sure the summarizer actually does it's thing
        time.sleep(10)
        
        # Check the database for new summary records.
        client = Elasticsearch()
        s = Search(using=client, index='gracc.osg.summary*') \
        .filter('range', **{'EndTime': {'from': 'now-7d', 'to': 'now'}}) \
        .params(search_type="count")
        
        response = s.execute()
        
        print response
        
        self.assertGreater(response.hits.total, 0)
        
        


