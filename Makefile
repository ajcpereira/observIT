SHELL := /bin/bash
LOG_PATH := $(PWD)/log


.PHONY: default
default: usage ;
usage:
	@echo "Usage:"
	@echo "make update_os"
	@echo "make setup"
	@echo "make setup_offline"
	@echo "make start"
	@echo "make stop"
	@echo "make remove"
	@echo "make update_logins"
	@echo "make update_theme"
	@echo "make update_datasource"
	@echo "make build_collector"
	@echo "make env_dev_ip"

.ONESHELL:
setup_offline:

	echo "##########################################################"
	echo "# We are assuming that the container images are already  #"
	echo "# in the system.                                         #"
	echo "#                                                        #"
	echo "##########################################################"
	@read -p "Press any key to continue"

	mkdir -p /opt/fjcollector/grafana/provisioning
	mkdir -p /opt/fjcollector/grafana/data/grafana
	mkdir -p /opt/fjcollector/collector/logs
	mkdir -p /opt/fjcollector/collector/config
	mkdir -p /opt/fjcollector/collector/keys
	mkdir -p /opt/fjcollector/collector/tests

	mkdir -p /opt/fjcollector/influxdb/influxdb
	mkdir -p /opt/fjcollector/influxdb/influxdb2
	mkdir -p /opt/fjcollector/influxdb/influxdb2-config

	chown -R  fjcollector:fjcollector /opt/fjcollector

	#cp ./install/Dockerfile .
	#docker build . -t fjcollector:latest

	docker compose up -d

	if [ ! -f /opt/fjcollector/collector/config/config.yaml ]
	then
	        cp config/config.yaml /opt/fjcollector/collector/config
	        chown fjcollector:fjcollector /opt/fjcollector/collector/config/config.yaml
	fi

	#rm Dockerfile

	echo "WILL PAUSE BEFORE CHANGE CONFIGFILE (30 secs)"

	sleep 30

	$(MAKE) update_logins
	$(MAKE) update_datasource
	$(MAKE) update_theme

	docker compose stop fjcollector
	docker compose start fjcollector

.ONESHELL:
setup:

	mkdir -p /opt/fjcollector/grafana/provisioning
	mkdir -p /opt/fjcollector/grafana/data/grafana
	mkdir -p /opt/fjcollector/collector/logs
	mkdir -p /opt/fjcollector/collector/config
	mkdir -p /opt/fjcollector/collector/keys
	mkdir -p /opt/fjcollector/collector/tests

	mkdir -p /opt/fjcollector/influxdb/influxdb
	mkdir -p /opt/fjcollector/influxdb/influxdb2
	mkdir -p /opt/fjcollector/influxdb/influxdb2-config

	chown -R  fjcollector:fjcollector /opt/fjcollector

	cp ./install/Dockerfile .

	docker build . -t fjcollector:latest

	docker compose up -d

	if [ ! -f /opt/fjcollector/collector/config/config.yaml ]
	then
	        cp config/config.yaml /opt/fjcollector/collector/config
	        chown fjcollector:fjcollector /opt/fjcollector/collector/config/config.yaml
	fi

	rm Dockerfile

	echo "WILL PAUSE BEFORE CHANGE CONFIGFILE (30 secs)"

	sleep 30

	$(MAKE) update_logins
	$(MAKE) update_datasource
	$(MAKE) update_theme

	docker compose stop fjcollector
	docker compose start fjcollector

.ONESHELL:
stop:
	docker compose stop

.ONESHELL:
update_os:
	sudo apt-get update && sudo apt-get upgrade -y

.ONESHELL:
remove:
	docker compose rm
	docker image rm grafana/grafana-enterprise
	docker image rm fjcollector
	docker image rm influxdb
	rm /opt/fjcollector/influxdb/influxdb2/influxd.bolt
	rm /opt/fjcollector/influxdb/influxdb2/influxd.sqlite

.ONESHELL:
start:
	docker compose up -d


.SILENT:
.ONESHELL:
update_logins:
	@
	echo "Going to reset admin password for grafana"
	@docker exec fjcollector-grafana-1 grafana cli admin reset-admin-password admin
	echo "##########################################################"
	echo "# Reset User and created service account for grafana     #"
	echo "# Please change the admin password we only               #"
	echo "# require the API token                                  #"
	echo "##########################################################"
	echo "Going to create service account for grafana"
	@RCURL=$$(curl -X POST http://admin:admin@localhost/api/serviceaccounts -H "Content-Type: application/json" -d '{"name":"fjcollector", "role":"Admin"}' 2>/dev/null | cut -d ":"  -f 2 | cut -d "," -f 1);
	echo $$RCURL

	if [[ $$RCURL =~ ^[0-9] ]]
	then
	        echo "Will create token"
	    @TCURL=$$(curl -X POST http://admin:admin@localhost/api/serviceaccounts/$$RCURL/tokens -H "Content-Type: application/json" -d '{"name":"fjcollector"}' 2>/dev/null | cut -d "," -f 3| cut -d ":" -f 2 | tr -d \} | tr -d \");
	        echo $$TCURL
	        if [ -f /opt/fjcollector/collector/config/config.yaml ] && [[ ! -z $TCURL ]]
	        then
	                sed -i "s/grafana_api_key\:.*/grafana_api_key\: $$TCURL/" /opt/fjcollector/collector/config/config.yaml
	                echo "Updated Config File with grafana api key"
	        else
	                echo "Failed to find the config file or get the token"
	        fi
	else
	        echo "Service account likely already exists, no changes made"
	fi


	echo "Setup and token update to grafana section is finished"


	echo "Going to create setup for influxdb"
	@docker exec fjcollector-influxdb-1 influx setup --org fjcollector --bucket fjcollector --username admin --password admin123 --retention 157w --force
	@TOKEN=$$(docker exec fjcollector-influxdb-1 influx auth ls | grep fjcollector | cut -f3)
	echo $$TOKEN
	if [[ -z $$TOKEN ]]
	then
	        echo "Will create token"
	        @TOKEN=$$(docker exec fjcollector-influxdb-1 influx auth create -o fjcollector --all-access --description "fjcollector" | grep fjcollector | cut -f3)
	        if [[ ! -z $$TOKEN ]]
	        then
	                sed -i "s/repository_api_key\:.*/repository_api_key\: $$TOKEN/" /opt/fjcollector/collector/config/config.yaml
	                echo "##############################################"
	                echo "# Please change the default admin pwd        #"
	                echo "# admin:admin123 we only required API token  #"
	                echo "##############################################"
	        else
	                echo "Failed to create a new token, solution will fail, manual intervention needed"
	        fi
	else
	        echo "Token already exists in influxdb"
	fi

	echo "Setup and token update to influxdb section is finished"

.ONESHELL:
update_theme:
	@
	#MYVAR=$$(docker inspect grafana -f '{{ .NetworkSettings.IPAddress }}' 2> /dev/null)
	#MYVAR=$$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fjcollector-grafana-1 2> /dev/null)
	RCURL=$$(curl -X PUT http://admin:admin@localhost/api/org/preferences -H "Content-Type: application/json" -d '{ "theme": "light" }' 2>/dev/null)

	if [ "$$RCURL" == "{\"message\":\"Preferences updated\"}" ]
	then
	        echo "Light Grafana default theme updated sucessfully"
	else
	        echo "Error updating grafana default theme: $$RCURL"
	fi

.ONESHELL:
update_datasource:
	@
	#MYVAR=$$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fjcollector-grafana-1 2> /dev/null)
	MYINFLUX="influxdb:8086"


	@TOKEN=$$(docker exec fjcollector-influxdb-1 influx auth ls | grep fjcollector | cut -f3)
	echo $$TOKEN

	if [[ ! -z $$TOKEN ]]
	then
	        RCURL=$$(curl -X POST http://admin:admin@localhost/api/datasources -H "Content-Type: application/json" -d '{"name": "InfluxDB","type": "influxdb","access": "proxy","url": "http://influxdb:8086","jsonData": {"dbName": "fjcollector","httpMode": "GET","httpHeaderName1": "Authorization"},"secureJsonData": {"httpHeaderValue1": "Token '$$TOKEN'"},"isDefault": true}' 2>/dev/null)
	        TEST=$$(grep 'Datasource added' <<< $$RCURL)
	else
	        echo "No Token was found, please check if the setup of the Influxdb was finished sucessfully"
	fi
	if [ -z "$$TEST" ]
	then
	        echo "Error creating grafana default datasource: $$RCURL"
	else
	        echo "Created Influxdb datasource (http://'$$MYINFLUX') in Grafana"
	fi


.ONESHELL:
build_collector:

	docker compose stop fjcollector

	docker compose images rm fjcollector-fjcollector-1

	cp ./install/Dockerfile .

	docker build . -t fjcollector:latest
	docker compose create fjcollector

	docker compose start fjcollector

	rm Dockerfile

.ONESHELL:
env_dev_ip:
	@
	MYVAR=$$(ip a | grep eth0 | grep inet | cut -f 1 -d"/" | cut -f 2 -d"t" )
	echo "$$MYVAR"
	sed -i "s/ip\:.*/ip\: $$MYVAR/" /opt/fjcollector/collector/config/config.yaml
	sed -i "s/ip_bastion\:.*/ip_bastion\: $$MYVAR/" /opt/fjcollector/collector/config/config.yaml
	sed -i "s/bastion\:.*/bastion\: $$MYVAR/" /opt/fjcollector/collector/config/config.yaml
