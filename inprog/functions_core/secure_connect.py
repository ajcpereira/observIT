import fabric2
import logging
import tempfile
#from pydantic.networks import IPvAnyAddress

class Secure_Connect():
    def __init__(self, param_ip, bastion, user, host_keys):
        
        logging.debug("Class Secure_connect Started")
        

        if bastion:
            logging.debug("Class Secure_connect with bastion Started")

            cmd_pkey_bastion = "cat $HOME/.ssh/id_rsa"
            try:
                logging.debug("Values ip %s, bastion %s, user %s and host_keys %s" % (param_ip, bastion, user, host_keys))
                self.ssh_bastion = fabric2.Connection(host=str(bastion), user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": host_keys,})
                self.ssh_bastion.open()
                logging.debug("Got session for bastion")
            except Exception as msgerror:
                logging.error("Failed fabric2 - %s" % msgerror)

            try:
                logging.debug("Will get pkey")
                
                pkey_bastion = self.ssh_bastion.run(cmd_pkey_bastion, hide=True).stdout.strip()
                pkey_trunk = pkey_bastion[0:50]
                
                logging.debug("Got the pkey %s" % pkey_trunk)
            
            except Exception as msgerror:
                logging.error("Failed to get pkey form bastion - %s" % msgerror)

            # Write the private key contents to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, buffering=- 1) as f:
                f.write(pkey_bastion.encode())
                private_key_file = f.name
        
            logging.debug("Wrote the key in temp file")

            try:
                self.ssh = fabric2.Connection(host=str(param_ip), user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": private_key_file,}, gateway=self.ssh_bastion)
                logging.debug("Created ssh connection with hostname - %s - through bastion - %s" % (param_ip, bastion))
            except Exception as msgerror:
                logging.error("Class Secure_Connect with bastion FAILED - %s" % msgerror)

            try:
                logging.debug("will open session")
                self.ssh.open()

                logging.debug("Class Secure_connect open ok, will return session - %s" % self)

            except Exception as msgerror:
               logging.error("Class Secure_Connect with bastion FAILED - %s" % msgerror)

        else:
            logging.debug("Class Secure_connect without bastion Started")
            try:
                self.ssh = fabric2.Connection(host=param_ip, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": host_keys,})

                self.ssh.open()
                
                logging.debug("Class Secure_connect ended, will return session - %s" % self)
                
            except Exception as msgerror:
                 logging.error("Class Secure FAILED - %s" % msgerror)

    def ssh_run(self, cmd):
         print(self)
         stdout = self.run(cmd)
         return stdout
    
    def ssh_del(self):
         print(self)
         self.close()