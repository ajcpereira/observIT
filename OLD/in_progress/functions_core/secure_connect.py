import fabric2
import logging
import time
import tempfile
import os
import threading

def create_single(hostname, user, host_keys):
    try:
        print("Opening Thread %s" % threading.current_thread())
        ssh = fabric2.Connection(host=hostname, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": host_keys,})
        ssh.open()
        return ssh
    except Exception as msg_error:
        print("Deu Er2ro no ssh %s" % msg_error)

def delete_single(ssh):
        ssh.close()
        print("Close Thread %s" % threading.current_thread())

class Secure_Connect():
    def __init__(self, param_ip, bastion, user, host_keys):
        try:
            logging.debug("%s - Function create_ssh Started - %s" % (threading.current_thread(),time.ctime()))
            self.ssh = fabric2.Connection(host=param_ip, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": host_keys,})
            self.ssh.open()
            print(self)
            logging.debug("%s - Function create_ssh ended, will return session - %s" % (threading.current_thread(),time.ctime()))
        #    return ssh
        except Exception as msg_error:
             logging.error("%s - Function create_ssh FAILED - %s - %s" % (threading.current_thread(), msg_error, time.ctime()))
    def ssh_run(self, cmd):
         stdout = self.ssh.run(cmd)
         return stdout
    def ssh_del(self):
         print(self)
         self.ssh.close()


# ssh-copy-id username@remote_host # Must be done previously
#def secure_connect(hostname,bastion,user,host_keys):
#
#    logging.debug("Function Secure_connect Started - %s - %s" % (threading.current_thread(),time.ctime()))
#
#    if bastion:
#        logging.debug("Will SSH through bastion - %s - %s" % (threading.current_thread(),time.ctime()))
#
#        try:
#            cmd_pkey_bastion = "cat $HOME/.ssh/id_rsa"
#            
#            ssh_bastion = fabric.Connection(host=hostname, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": host_keys,})
#            
#            logging.debug("Created ssh connection with bastion - %s - %s" % (threading.current_thread(),time.ctime()))
#            pkey_bastion = ssh_bastion.run(cmd_pkey_bastion, hide=True).stdout.strip()
#            logging.debug("Got the key to make ssh to the host")
#            
#            # Write the private key contents to a temporary file
#            with tempfile.NamedTemporaryFile(delete=False, buffering=- 1) as f:
#                f.write(pkey_bastion.encode())
#                private_key_file = f.name
#            
#            logging.info("Wrote the key in temp file - %s - %s" % (threading.current_thread(),time.ctime()))
#            ssh = Connection(hostname, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": private_key_file,}, gateway=ssh_bastion)
#            logging.debug("Created ssh connection with hostname - %s - through bastion - %s - %s" % (hostname,threading.current_thread(),time.ctime()))
#		
#
#            logging.debug("Finished function through bastion - %s - %s" % (threading.current_thread(),time.ctime()))
#            return ssh
#
#
#        except Exception as msg_err:
#            logging.error("Error connectiong to " + bastion + " or " + hostname + " on port 22" + " with error " + str(msg_err))
#            exit(1)
#        
#        f.close()
#        os.remove(f.name)
#        
#        
#
#	
#    else:
#        logging.debug("Will SSH without bastion - %s - %s" % (threading.current_thread(),time.ctime()))
#        try:
#            ssh = fabric.Connection(host=hostname, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": host_keys,})
#            ssh.open()
#            logging.debug("This is the ssh session %s - %s - %s" % (ssh, threading.current_thread(), time.ctime()))
#            return ssh
#        except Exception as msg_err:
#            logging.error("Error connectiong to " + hostname + " on port 22" + " with error " + str(msg_err) + "%s - %s" % (threading.current_thread(),time.ctime()))
#            exit(1)