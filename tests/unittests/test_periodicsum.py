
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
        
        
        # Update the EndTimes
        for hit in s[:100]:
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
            
            client.index(index="gracc.osg.raw0-now", doc_type='JobUsageRecord', body=hit.to_dict())

            #to_upload.append(hit)
        
        
    
    def test_raw_data(self):
        """
        Testing the tester!
        """
        
        # Check the raw indexes for records from the last 7 days
        client = Elasticsearch()
        s = Search(using=client, index='gracc.osg.raw0-*') \
        .filter('range', **{'EndTime': {'from': 'now-7d', 'to': 'now'}}) \
        .params(search_type="count")
        
        response = s.execute()
        
        print response
        print response.hits.total
        
        self.assertGreater(response.hits.total, 0)

        
    def test_periodic_summarizer(self):
        
        # Restart the graccsumperiodic service 
        subprocess.call("systemctl restart graccsumperiodic.service", shell=True)
        
        # Wait for a bit to make sure the summarizer actually does it's thing
        time.sleep(60)
        
        # Check the database for new summary records.
        client = Elasticsearch()
        
        # Refresh the indexes
        client.indices.refresh(index='gracc.osg.summary*')
        time.sleep(10)
        
        # Search for the summary records
        s = Search(using=client, index='gracc.osg.summary*') \
        .filter('range', **{'EndTime': {'from': 'now-7d', 'to': 'now'}}) \
        .params(search_type="count")
        
        response = s.execute()
        
        print response
        print response.hits.total
        
        self.assertGreater(response.hits.total, 0)
        
        


