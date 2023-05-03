from fabric import Connection
from functions.fs import fs
import logging
import time
import os

# ssh-copy-id username@remote_host # Must be done previously
def secure_connect(hostname,bastion,user, type, host_keys, know_hosts, PLATFORM, PLATFORM_NAME, PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL, PLATFORM_USE_SUDO):
	log_stamp=time.time()
		
	if bastion:
		logging.info("Will SSH through bastion - %s" % log_stamp)

		##############################
		##############################
		#### NEED REVIEW #############
		##############################
		ssh = Connection(hostname, user=user, port=22, connect_timeout=10, connect_kwargs={'key_filename': os.environ['PRIVATE_KEY_TO_HOST']},
		   gateway=Connection(host=bastion, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": host_keys,}))
		logging.debug(ssh)
		eval(type)(hostname, ssh, PLATFORM, PLATFORM_NAME, type, PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL, PLATFORM_USE_SUDO)
		ssh.close()
		logging.info("Finished SSH through bastion - %s" % log_stamp)
	else:
		logging.info("Will SSH without bastion - %s" % log_stamp)
		ssh = Connection(host=hostname, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": host_keys,})
		logging.debug(ssh)
		eval(type)(hostname, ssh, PLATFORM, PLATFORM_NAME, type, PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL, PLATFORM_USE_SUDO)
		ssh.close()
		logging.info("Finished SSH without bastion - %s" % log_stamp)
