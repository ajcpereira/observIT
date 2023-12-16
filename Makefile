SHELL := /bin/bash
LOG_PATH := $(PWD)/log


.PHONY: default
default: usage ;
usage:
	@echo "Usage:"
	@echo "make setup"
	@echo "make start"
	@echo "make stop"
	@echo "make remove"
	@echo "make update_logins"
	@echo "make update_theme"
	@echo "make update_datasource"
	@echo "make build_collector"

	
.ONESHELL:
setup:
	
	mkdir -p /opt/fj-collector/graphite/data/storage
	mkdir -p /opt/fj-collector/graphite/data/statsd_config
	mkdir -p /opt/fj-collector/graphite/data/conf
	mkdir -p /opt/fj-collector/grafana/provisioning
	mkdir -p /opt/fj-collector/grafana/data/grafana
	mkdir -p /opt/fj-collector/collector/logs
	mkdir -p /opt/fj-collector/collector/config
	mkdir -p /opt/fj-collector/collector/keys
	mkdir -p /opt/fj-collector/collector/tests

	mkdir -p /opt/fj-collector/influxdb/influxdb
	mkdir -p /opt/fj-collector/influxdb/influxdb2
	mkdir -p /opt/fj-collector/influxdb/influxdb2-config

	chown -R  fjcollector:fjcollector /opt/fj-collector
	
	cp ./install/Dockerfile .

	docker build . -t fj-collector:latest

	docker compose up -d

	if [ ! -f /opt/fj-collector/collector/config/config.yaml ]
	then
		cp config/config.yaml /opt/fj-collector/collector/config
		chown fjcollector:fjcollector /opt/fj-collector/collector/config/config.yaml
	fi

	rm Dockerfile

	if [ -f /opt/fj-collector/graphite/data/conf/carbon.conf ]
	then
		sed -i "s/MAX_UPDATES_PER_SECOND.*/MAX_UPDATES_PER_SECOND \= 5000/" /opt/fj-collector/graphite/data/conf/carbon.conf
		sed -i "s/MAX_CREATES_PER_MINUTE.*/MAX_CREATES_PER_MINUTE \= 5000/" /opt/fj-collector/graphite/data/conf/carbon.conf
		echo "Updated Graphite Config File"
	fi


	if [ -f /opt/fj-collector/graphite/data/conf/storage-schemas.conf ]
	then
		sed -i "s/retentions = 10s:6h,1m:6d,10m:1800d/retentions = 1m:6d,5m:30d,15m:1800d/" /opt/fj-collector/graphite/data/conf/storage-schemas.conf
		echo "Updated Graphite Schema File"
	fi


	docker compose stop graphite
	docker compose start graphite

	echo "WILL PAUSE BEFORE CHANGE CONFIGFILE (30 secs)"

	sleep 30

	$(MAKE) update_logins
	$(MAKE) update_datasource
	$(MAKE) update_theme

	docker compose stop fj-collector
	docker compose start fj-collector

.ONESHELL:
stop:
	docker compose stop

.ONESHELL:
remove:
	docker compose rm
	docker image rm graphiteapp/graphite-statsd
	docker image rm grafana/grafana-enterprise
	docker image rm fj-collector
	docker image rm influxdb

.ONESHELL:
start:
	docker compose up -d


.SILENT:
.ONESHELL:
update_logins:
	@
	MYVAR=$$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fj-collector-grafana-1 2> /dev/null)
	echo $$MYVAR
	if [[ ! -z $$MYVAR ]]
	then
		echo "Going to reset admin password for grafana"
		@docker exec fj-collector-grafana-1 grafana cli admin reset-admin-password admin
		echo "##########################################################"
		echo "# Reseted User and created service account for grafana   #"
		echo "# Please change the admin password we only               #"
		echo "# require the API token                                  #"
		echo "##########################################################"
		echo "Going to create service account for grafana"
		@RCURL=$$(curl -X POST http://admin:admin@$$MYVAR/api/serviceaccounts -H "Content-Type: application/json" -d '{"name":"fj-collector", "role":"Admin"}' 2>/dev/null | cut -d ":"  -f 2 | cut -d "," -f 1);
		echo $$RCURL
		
		if [[ $$RCURL =~ ^[0-9] ]]
		then
			echo "Will create token"
		    @TCURL=$$(curl -X POST http://admin:admin@$$MYVAR/api/serviceaccounts/$$RCURL/tokens -H "Content-Type: application/json" -d '{"name":"fj-collector"}' 2>/dev/null | cut -d "," -f 3| cut -d ":" -f 2 | tr -d \} | tr -d \");
			echo $$TCURL
			if [ -f /opt/fj-collector/collector/config/config.yaml ] && [[ ! -z $TCURL ]]
			then
				sed -i "s/grafana_api_key\:.*/grafana_api_key\: $$TCURL/" /opt/fj-collector/collector/config/config.yaml
				echo "Updated Config File with grafana api key"
			else
				echo "Failed to find the config file or get the token"
			fi
		else
			echo "Service account likely already exists, no changes made"
		fi
	else
		echo "Failed to find the grafana container IP"
	fi

	echo "Setup and token update to grafana section is finished"

	MYVAR=$$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fj-collector-influxdb-1 2> /dev/null)
	echo $$MYVAR
	if [[ ! -z $$MYVAR ]]
	then
		echo "Going to create setup for influxdb"
		@docker exec fj-collector-influxdb-1 influx setup --org fjcollector --bucket fjcollector --username admin --password admin123 --retention 157w --force
		@TOKEN=$$(docker exec fj-collector-influxdb-1 influx auth ls | grep fjcollector | cut -f3)
		echo $$TOKEN

		if [[ -z $$TOKEN ]]
		then
			echo "Will create token"
			@TOKEN=$$(docker exec fj-collector-influxdb-1 influx auth create -o fjcollector --all-access --description "fjcollector" | grep fjcollector | cut -f3)
			if [[ ! -z $$TOKEN ]]
			then
				sed -i "s/repository_api_key\:.*/repository_api_key\: $$TOKEN/" /opt/fj-collector/collector/config/config.yaml
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
	else
	   	echo "Failed to find the influxdb container IP"
	fi

	echo "Setup and token update to influxdb section is finished"

.ONESHELL:
update_theme:
	@
	#MYVAR=$$(docker inspect grafana -f '{{ .NetworkSettings.IPAddress }}' 2> /dev/null)
	MYVAR=$$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fj-collector-grafana-1 2> /dev/null)
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
	#MYVAR=$$(docker inspect grafana -f '{{ .NetworkSettings.IPAddress }}' 2> /dev/null)
	MYVAR=$$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fj-collector-grafana-1 2> /dev/null)
	#MYGRAPHITE=$$(docker inspect graphite -f '{{ .NetworkSettings.IPAddress }}' 2> /dev/null)
	#MYGRAPHITE=$$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fj-collector-graphite-1 2> /dev/null)
	MYGRAPHITE="graphite"
	RCURL=$$(curl -X POST http://admin:admin@localhost/api/datasources -H "Content-Type: application/json" -d '{ "name":"Graphite", "type":"graphite", "url":"http://'$$MYGRAPHITE'", "access":"proxy", "isdefault":true }' 2>/dev/null)
	TEST=$$(grep 'Datasource added' <<< $$RCURL)

	if [ -z "$$TEST" ]
	then
		echo "Error creating grafana default datasource: $$RCURL"
	else
		echo "Created Graphite datasource (http://'$$MYGRAPHITE') in Grafana"
	fi


.ONESHELL:
build_collector:

	cp ./install/Dockerfile .
	docker build . -t fj-collector:latest


	docker compose start fj-collector

	rm Dockerfile
