import sys
sys.path.append("functions")
import yaml
import time
from functions.secure_connect import secure_connect
import schedule
import logging

configfile = "/collector/fj-collector/config/collector.yml"
#configfile = "/home/ajcpereira/git/reporting/collector/config/collector.yml"

# Read the YAML file
with open(configfile, 'r') as f:
  try:
    configdata = yaml.safe_load(f)
    f.close
  except FileNotFoundError:
    print("Sorry, the file %s does not exist" % configfile)

# CREATE CONSTANTS BASED IN PARAMETERS FROM YAML
  PLATFORM_REPO=configdata["parameters"]["repository"]
  PLATFORM_REPO_PORT=configdata["parameters"]["repository_port"]
  PLATFORM_REPO_PROTOCOL=configdata["parameters"]["repository_protocol"]
  PLATFORM_HOSTKEYS=configdata["parameters"]["host_keys"]
  PLATFORM_USE_SUDO=configdata["parameters"]["use_sudo"]
  PLATFORM_KNOW_HOSTS=configdata["parameters"]["known_hosts"]
  PLATFORM_LOG="logging." + configdata["parameters"]["log"]

#logging.basicConfig(filename='/collector/fj-collector/logs/fj-collector.log', encoding='utf-8', level=logging.INFO)
logging.basicConfig(filename='/collector/fj-collector/logs/fj-collector.log', level=eval(PLATFORM_LOG))
# Default Filename for configuration


# PROCESS AND EXECUTE EACH LINE FROM YAML
log_stamp=time.time()

logging.info("Starting YAML Processing- %s" % log_stamp)

for i in range(len(configdata['solution']['platform'])):
  if configdata['solution']['platform'][i]['type'] == "CS8000":
    PLATFORM=(configdata['solution']['platform'][i]['type'])
    PLATFORM_NAME=(configdata['solution']['platform'][i]['name'])
    for z in range(len(configdata['solution']['platform'][i]['resources']['type'])):
      if configdata['solution']['platform'][i]['resources']['type'][z] == "fs":
        for x in range(len(configdata['solution']['platform'][i]['resources']['ip'])):
          var_configdata_current=configdata['solution']['platform'][i]['resources']
          schedule.every(var_configdata_current["poll"]*60).seconds.do(secure_connect, var_configdata_current["ip"][x], var_configdata_current["proxy"], var_configdata_current["user"], var_configdata_current["type"][z], PLATFORM_HOSTKEYS, PLATFORM_KNOW_HOSTS, PLATFORM, PLATFORM_NAME, PLATFORM_REPO, PLATFORM_REPO_PORT, PLATFORM_REPO_PROTOCOL, PLATFORM_USE_SUDO)
      elif configdata['solution']['platform'][i]['resources']['type'][z] == "channel":
        for x in range(len(configdata['solution']['platform'][i]['resources']['ip'])):
          print("channel" + configdata['solution']['platform'][i]['resources']['ip'])
      else:
          print("No valid option for type")
logging.info("Finished YAML Processing- %s" % log_stamp)

while True:
    schedule.run_pending()
    time.sleep(1)
