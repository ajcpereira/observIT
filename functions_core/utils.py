import logging, base64

#args=args_setup(args)
def args_setup(args):

    logging.debug("utils lib outpu from arg dict %s" % args)
    if args['ip_bastion']:
          bastion=str(args['ip_bastion'])
    elif args['bastion']:
          bastion=str(args['bastion'])
    else:
          bastion=None

    if args['ip_host_keys']:
          host_keys=args['ip_host_keys']
    elif args['host_keys']:
          host_keys=args['host_keys']
    else:
          host_keys=None

    if args['alias']:
        hostname = args['alias']
    else:
        hostname = str(args['ip'])

    if args['ip_redfish_url']:
         redfish_url=str(args['ip_redfish_url'])
    elif args['redfish_url']:
         redfish_url=str(args['redfish_url'])
    else:
         redfish_url=None
         
    if args['ip_redfish_proxy']:
         redfish_proxy=str(args['ip_redfish_proxy'])
    elif args['redfish_proxy']:
         redfish_proxy=str(args['redfish_proxy'])
    else:
         redfish_proxy=None

    if args['ip_redfish_user']:
         redfish_user=str(args['ip_redfish_user'])
    elif args['redfish_user']:
         redfish_user=str(args['redfish_user'])
    else:
         redfish_user=None

    if args['ip_redfish_pwd64']:
         redfish_pwd64=str(args['ip_redfish_pwd64'])
    elif args['redfish_pwd64']:
         redfish_pwd64=str(args['redfish_pwd64'])
    else:
         redfish_pwd64=None

    if args['ip_redfish_unsecured']:
         redfish_unsecured=str(args['ip_redfish_unsecured'])
    elif args['redfish_unsecured']:
         redfish_unsecured=str(args['redfish_unsecured'])
    else:
         redfish_unsecured=None

    args['bastion']=bastion
    args['host_keys']=host_keys
    args['hostname']=hostname
    args['redfish_url']=redfish_url
    args['redfish_proxy']=redfish_proxy
    args['redfish_user']=redfish_user
    args['redfish_pwd64']=redfish_pwd64
    args['redfish_unsecured']=redfish_unsecured
    
    return args

def decode_base64(base64_message):
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')

    return message