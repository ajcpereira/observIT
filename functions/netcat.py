import socket
import logging
#import time


def netcat(graphite_srv, port, protocol, text):
    #log_stamp=time.time()

    #logging.info("Starting netcat - %s" % log_stamp)
    #logging.info(text)

    if protocol == "tcp":
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((graphite_srv, port))
            s.sendall(text.encode('utf-8'))
        except Exception as msg_err:
            print ("Error connectiong to " + graphite_srv + " on port " + str(port) + " on protocol " + protocol + " with error " + str(msg_err))
        finally:
            s.close()
    elif protocol == "udp":
        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.sendto(text.encode('utf-8'), (graphite_srv, port))
        except Exception as msg_err:
            print ("Error connectiong to " + graphite_srv + " on port " + str(port) + " on protocol " + protocol + " with error " + str(msg_err))
        finally:
            s.close()
    else:
        print("No valid protocol selected")

    #logging.info("Finished netcat - %s" % log_stamp)        