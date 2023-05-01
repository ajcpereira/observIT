import paramiko
from functions.fs import fs
import logging
import time


# ssh-copy-id username@remote_host # Must be done previously
def secure_connect(hostname,bastion,user, type, host_keys, know_hosts, PLATFORM, PLATFORM_NAME, PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL, PLATFORM_USE_SUDO):
	log_stamp=time.time()
	try:
		ssh = paramiko.SSHClient()
		#ssh.load_system_host_keys(know_hosts)
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		#ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
	except Exception as e:
		print(e)
		
	if bastion:
		print("Have a bastion")
#   		#client = paramiko.SSHClient()
#   		#client.load_system_host_keys()
#   		#client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#  	 		# Create a transport to the bastion
#			#bastion_transport = paramiko.Transport((proxy, 22))
#   		# Connect to the bastion using the user and keys
#   		#bastion_transport.connect(username=user)
#   		# Create a connection to the IP using the bastion
#   		#ip_transport = paramiko.Transport(ip, 22)
#   		#ip_transport.connect(username=user, sock=bastion_transport)
#   		# Create the client
#   		#ssh = paramiko.SSHClient()
#   		#ssh.load_system_host_keys()
#   		#ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#   		# Connect to the IP
#   		#ssh.connect(ip, username=user, sock=ip_transport)
#	    # Return the client
#		# return client
	else:
		logging.info("Will SSH without proxy - %s" % log_stamp)
		pkey = paramiko.RSAKey.from_private_key_file(host_keys)
		ssh.connect(hostname, username=user, pkey=pkey, look_for_keys=False, auth_timeout=5, timeout=10)
		eval(type)(hostname, ssh, PLATFORM, PLATFORM_NAME, type, PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL, PLATFORM_USE_SUDO)
		ssh.close()
		logging.info("Finished SSH without proxy - %s" % log_stamp)
