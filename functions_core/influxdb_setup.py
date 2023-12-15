import requests
import logging

########## FUNCTION CREATE SETUP FOR INFLUXDB  ##################################
def influxdb_setup(config):

    config.global_parameters.repository_org
    config.global_parameters.collector_root
    config.global_parameters.repository
    try:
        if os.path.isfile(configfile):
            logging.debug("Using default configfile config/config.yaml")
            config = read_yaml(configfile)
            orig_mtime=(os.path.getmtime(configfile))
    except Exception as msgerr:
            logging.error("Can't handle configfile - %s - with error - %s" % (configfile,msgerr))
            sys.exit()

    #sys.exit("No configfile could be found")
        
########## FUNCTION CREATE SETUP FOR INFLUXDB  ##################################
            

    headers = {'Authorization': f"Bearer {api_key}", 'Content-Type': 'application/json'}

    try:
        r = requests.post(f"http://{server}/api/dashboards/db", data=json, headers=headers, verify=verify)
    except:
        logging.error("Unable to create dashboard in grafana!")
        logging.error("Status code = %s", r.status_code)
        logging.error("Response = %s", r.content)


influx bucket create \
  --name <bucket-name> \
  --org <org-name> \
  --retention <retention-period-duration>

157 weeks


influx setup --org fjcollector --bucket fjcollector --username admin --password admin123 --retention 157w --force

/opt/fj-collector/influxdb/influxdb2

influxd.bolt
influxd.sqlite


curl --request GET         "http://localhost:8086/api/v2/authorizations"   --header "Authorization: Token tJblSQ3L6Yw4iXdd4iEeAdtMPBkEVURHZSvRw1QSEgzXyK6TzoNNbDsHOoNiCgtbJtT2K4vqanMb6r1UF8DwQ=="   --header 'Content-type: application/json'