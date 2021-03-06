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



class TestSummarizer(unittest.TestCase):
    
    def setUp(self):
        """
        Setup the indexes
        """
        
        # Restart the graccsumperiodic service 
        subprocess.call("systemctl stop graccsumperiodic.timer", shell=True)
        
        # Remove all of the summary indexes from elasticsearch
        client = Elasticsearch()
        client.indices.delete("gracc.osg.summary*")
        
    def _getCount(self):
        client = Elasticsearch()
        client.indices.refresh(index='gracc.osg.summary*')
        s = Search(using=client, index='gracc.osg.summary*') \
        .filter('range', **{'EndTime': {'from': '2016-01-01', 'to': '2017-01-01'}})
        

        return s.count()

        
    def test_OneDay(self):
        "Test 1 day worth of data"
        
        subprocess.call("graccsummarizer amqp://localhost/ \"2016-06-21\" \"2016-06-23\"", shell=True)
        
        time.sleep(20)
        
        self.assertGreater(self._getCount(), 0)
        
        
    def test_SevenDay(self):
        "Test 7 Days worth of data"
        subprocess.call("graccsummarizer amqp://localhost/ \"2016-06-20\" \"2016-06-27\"", shell=True)
        
        time.sleep(20)
                
        self.assertGreater(self._getCount(), 0)
    
    def test_ThirtyDays(self):
        "Test 30 days worth of data"
        subprocess.call("graccsummarizer amqp://localhost/ \"2016-06-01\" \"2016-07-01\"", shell=True)
        
        time.sleep(20)
                
        self.assertGreater(self._getCount(), 0)
        
        
    def test_OneYear(self):
        """
        Test 1 year worth of data
        Takes too long to run 1 year, so just do ~3 months
        """
        subprocess.call("graccsummarizer amqp://localhost/ \"2016-05-01\" \"2016-08-01\"", shell=True)
        
        time.sleep(20)
        client = Elasticsearch()
        stats = client.cat.indices(index='_all')
        print stats
                
        self.assertGreater(self._getCount(), 0)
        
        