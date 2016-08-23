from graccreq import Client
import argparse
from dateutil.parser import parse
import datetime





def main():
    # Read the command line arguments
    parser = argparse.ArgumentParser(description="Force summarization for a given time period")
    
    parser.add_argument('from_str', metavar='from', help="Dateutil parsable date beginning of summarization period")
    parser.add_argument('to_str', metavar='to', help="Dateutil parsable date end of summarization period")
    
    # Arguments for the AMQP
    parser.add_argument('--exchange', dest='exchange', help="Exchange to send summarize request", default="gracc.osg.requests")
    parser.add_argument('--routing_key', dest='routing_key', help="Routing key to use for summarize request", default="gracc.osg.requests")
    parser.add_argument('--host', dest='host', help="Host of AMQP broker", default="localhost")
    parser.add_argument('--vhost', dest='vhost', help="Virtual host for the AMQP server", default="/")
    parser.add_argument('--username', dest='username', help="Username for AMQP broker", default="guest")
    parser.add_argument('--password', dest='password', help="Password for AMQP broker", default="guest")
    
    # Arguments to send to the remote summarizer
    parser.add_argument('--destination_exchange', dest='destination_exchange', help="Exchange to send summarized records", default="gracc.osg.summary")
    parser.add_argument('--destination_key', dest='destination_key', help="Routing key to send summarized records", default="gracc.osg.summary")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Create the client
    client = Client(exchange=args.exchange, routing_key=args.routing_key, host=args.host, username=args.username, password=args.password, vhost=args.vhost)
    
    # Break the summarize period into 7 day increments, so we don't overload anything!
    # (no testing went into this decision, 7 days was picked arbitrarily)
    from_date = parse(args.from_str)
    to_date = parse(args.to_str)
    
    while (from_date < to_date):
        tmp_to_date = min(from_date + datetime.timedelta(days=7), to_date)
        print "Summarizing %s to %s" % (from_date.isoformat(), tmp_to_date.isoformat())
        client.query(from_date, tmp_to_date, 'summary', destination_exchange=args.destination_exchange, destination_key=args.destination_key)
        
        # Update the from date
        from_date = tmp_to_date
    


if __name__ == "__main__":
    main()

