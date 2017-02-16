
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
        client = Elasticsearch(index='gracc.osg.raw-*')
        s = Search(using=client)
        s.query("match_all")
        response = s.execute()
        to_upload = []
        
        # Get one of the raw indices' mapping, and copy it here
        mapping = client.indices.get_mapping(index='gracc.osg.raw-2016.07')
        #print mapping
        client.indices.delete(index='gracc.osg.raw-now', ignore=404)
        client.indices.create(index='gracc.osg.raw-now', body=mapping['gracc.osg.raw-2016.07'])
        
        # Update the EndTimes
        for hit in s[:100]:
            #print hit.EndTime
            # Determine the number of days between the current EndTime and now
            try:
                cur_endtime = dateutil.parser.parse(hit.EndTime)
                diff = datetime.datetime.now(utc) - cur_endtime
                cur_starttime = dateutil.parser.parse(hit.StartTime)
            except:
                # Sometimes the endtime is list
                print hit
                print "EndTime is list"
                continue
            #print "Difference in days is %i" % diff.days
            # Randomly subtract between 0-6 days from the EndTime
            diff -= datetime.timedelta(days=random.randint(0,6))
            #print "New difference in days is %i" % diff.days
            
            # Update the new EndTime and add to upload
            hit.EndTime = (cur_endtime + diff).isoformat()
            hit.StartTime = (cur_starttime + diff).isoformat()
            #print "New endtime is %s" % str(hit.EndTime)
            #print "New starttime is %s" % str(hit.StartTime)
            
            client.index(index="gracc.osg.raw-now", doc_type='JobUsageRecord', body=hit.to_dict())

            #to_upload.append(hit)
            
        # Connect and query the elasticsearch database
        client = Elasticsearch(index='gracc.osg-transfer.raw-*')
        s = Search(using=client)
        s.query("match_all")
        response = s.execute()
        to_upload = []
        
        # Get one of the raw indices' mapping, and copy it here
        mapping = client.indices.get_mapping(index='gracc.osg-transfer.raw-2016.06')
        #print mapping
        client.indices.delete(index='gracc.osg-transfer.raw-now', ignore=404)
        client.indices.create(index='gracc.osg-transfer.raw-now', body=mapping['gracc.osg-transfer.raw-2016.06'])
        
        # Update the EndTimes
        for hit in s[:100]:
            #print hit.EndTime
            # Determine the number of days between the current EndTime and now
            try:
                cur_endtime = dateutil.parser.parse(hit.EndTime)
                diff = datetime.datetime.now(utc) - cur_endtime
                cur_starttime = dateutil.parser.parse(hit.StartTime)
            except:
                # Sometimes the endtime is list
                print hit
                print "EndTime is list"
                continue
            #print "Difference in days is %i" % diff.days
            # Randomly subtract between 0-6 days from the EndTime
            diff -= datetime.timedelta(days=random.randint(0,6))
            #print "New difference in days is %i" % diff.days
            
            # Update the new EndTime and add to upload
            hit.EndTime = (cur_endtime + diff).isoformat()
            hit.StartTime = (cur_starttime + diff).isoformat()
            #print "New endtime is %s" % str(hit.EndTime)
            #print "New starttime is %s" % str(hit.StartTime)
            
            client.index(index="gracc.osg-transfer.raw-now", doc_type='JobUsageRecord', body=hit.to_dict())

        
        
    
    def test_raw_data(self):
        """
        Testing the tester!
        """
        
        # Check the raw indexes for records from the last 7 days
        client = Elasticsearch()
        s = Search(using=client, index='gracc.osg.raw0-*') \
        .filter('range', **{'EndTime': {'from': 'now-7d', 'to': 'now'}})
    
        
        num_raw = s.count()
        
        stats = client.cat.indices(index='_all')
        print stats
        
        self.assertGreater(num_raw, 0)
        
        
    def test_raw_transfer(self):
        """
        Testing the tester for raw summary data
        """
        # Check the raw indexes for records from the last 7 days
        client = Elasticsearch()
        s = Search(using=client, index='gracc.osg-transfer.raw*') \
        .filter('range', **{'StartTime': {'from': 'now-7d', 'to': 'now'}})
        
        num_raw = s.count()
        
        stats = client.cat.indices(index='_all')
        print stats
        
        self.assertGreater(num_raw, 0)

        
    def test_periodic_summarizer(self):
        
        # Check the database for new summary records.
        client = Elasticsearch()
        
        # Refresh the indexes
        client.indices.refresh(index='gracc.osg.raw*')
        
        # Restart the graccsumperiodic service 
        subprocess.call("systemctl restart graccsumperiodic.service", shell=True)
        
        # Wait for a bit to make sure the summarizer actually does it's thing
        time.sleep(60)
        
        # Refresh the indexes
        client.indices.refresh(index='gracc.osg.summary*')
        time.sleep(60)
        
        # Search for the summary records
        s = Search(using=client, index='gracc.osg.summary*') \
        .filter('range', **{'EndTime': {'from': 'now-7d', 'to': 'now'}})
        
        num_sum = s.count()
        
        stats = client.cat.indices(index='_all')
        print stats
        
        self.assertGreater(num_sum, 0)
        
        # Search for the summary transfer records
        s = Search(using=client, index='gracc.osg.transfer-summary*') \
        .filter('range', **{'StartTime': {'from': 'now-7d', 'to': 'now'}})
        
        num_sum = s.count()
        
        self.assertGreater(num_sum, 0)
        


if __name__ == "__main__":
    unittest.main()


