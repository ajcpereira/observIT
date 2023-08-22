import logging

def fs_name(**args):
    print("*********************ENTROU***************************")
    # Get variables from args
    print(args)
    print(args['resources_types'])
    logging.info("IP %s" % args['ip'])
