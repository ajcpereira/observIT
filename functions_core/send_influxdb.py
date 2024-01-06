
from influxdb_client.client.write_api import SYNCHRONOUS
import logging
import influxdb_client


def send_influxdb(srv, port, token, org, bucket, data):

    logging.debug("Sending data to InfluxDB server: %s", srv)

    try:
        write_client = influxdb_client.InfluxDBClient(url="http://" + srv + ":" + port, token=token, org=org,timeout=10000, enable_gzip=True)
        write_api = write_client.write_api(write_options=SYNCHRONOUS)
        response = write_api.write(bucket=bucket, org=org, record=data,write_precision="s")
        if response:
            logging.error("Received msg from Influxdb during write to server %s with msg %s" % (srv,response)) # response is None if there is no error
        
        write_client.close()

    except Exception as msgerror:
        logging.error("Failed to send data to InfluxDB %s - error %s" % (srv, msgerror))

