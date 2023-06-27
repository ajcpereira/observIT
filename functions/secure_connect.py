from fabric import Connection
from functions.fs import fs
import logging
import time
import tempfile
import os

# ssh-copy-id username@remote_host # Must be done previously
def secure_connect(hostname,bastion, user, type, host_keys, know_hosts, PLATFORM, PLATFORM_NAME, PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL, PLATFORM_USE_SUDO):
    log_stamp=time.ctime()
    logging.info("Function Secure_connect Started - %s" % log_stamp)

    if bastion:
        logging.info("Will SSH through bastion - %s" % log_stamp)

        try:
            cmd_pkey_bastion = "cat /home/" + user + "/.ssh/id_rsa"
            ssh_bastion = Connection(host=bastion, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": host_keys,})
            logging.info("Created ssh connection with bastion - %s" % bastion)
            pkey_bastion = ssh_bastion.run(cmd_pkey_bastion, hide=True).stdout.strip()
            logging.info("Got the key to make ssh to the host")
            # Write the private key contents to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, buffering=- 1) as f:
                f.write(pkey_bastion.encode())
                private_key_file = f.name
            logging.info("Wrote the key in temp file")
            ssh = Connection(hostname, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": private_key_file,}, gateway=ssh_bastion)
            logging.info("Created ssh connection with hostname - %s - through bastion" % hostname)
		
            logging.info("Created ssh connection with bastion will execute function - %s" % type)
            eval(type)(hostname, ssh, PLATFORM, PLATFORM_NAME, type, PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL, PLATFORM_USE_SUDO)
            logging.info("Finished function through bastion - %s" % log_stamp)

            ssh_bastion.close()
            ssh.close()
            f.close()
            os.remove(f.name)

        except Exception as msg_err:
            logging.error("Error connectiong to " + bastion + " or " + hostname + " on port 22" + " with error " + str(msg_err))

	
    else:
	
        logging.info("Will SSH without bastion - %s" % log_stamp)

        ssh = Connection(host=hostname, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": host_keys,})

        logging.debug(ssh)

        eval(type)(hostname, ssh, PLATFORM, PLATFORM_NAME, type, PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL, PLATFORM_USE_SUDO)
        ssh.close()

        logging.info("Finished SSH without bastion - %s" % log_stamp)
