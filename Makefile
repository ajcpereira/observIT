SHELL := /bin/bash
LOG_PATH := $(PWD)/log


.PHONY: default
default: usage ;
usage:
	@echo "Usage:"
	@echo "make install"
	@echo "make start"
	@echo "make stop"
	@echo "make remove"
	@echo "make update_addr"
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
	
	cp ./install/Dockerfile .
	podman build . -t fj-collector:latest

	podman pull docker.io/graphiteapp/graphite-statsd
	podman pull docker.io/grafana/grafana-enterprise

	if [ ! -f /opt/fj-collector/collector/config/config.yaml ]
	then
		cp config/config.yaml /opt/fj-collector/collector/config
	fi
	
	podman run -d \
 	--name graphite \
 	--restart=always \
 	-p 80:80/tcp \
	-p 12003:2003/tcp \
	-p 18125:8125/udp \
	-v /etc/localtime:/etc/localtime:ro \
	-v /opt/fj-collector/graphite/data/conf:/opt/graphite/conf \
	-v /opt/fj-collector/graphite/data/storage:/opt/graphite/storage \
	-v /opt/fj-collector/graphite/data/statsd_config:/opt/statsd/config \
	--log-opt max-size=10m --log-opt max-file=3 \
	graphiteapp/graphite-statsd

	podman run -d \
	--name grafana \
    --restart=always \
    -p 3000:3000/tcp \
    -v /opt/fj-collector/grafana/provisioning/:/etc/grafana/provisioning/ \
    -v /opt/fj-collector/grafana/data/grafana:/var/lib/grafana/ \
    -u 0 \
	--log-opt max-size=10m --log-opt max-file=3 \
	grafana/grafana-enterprise
	
	podman run -d \
	--name fj-collector \
	--restart=always \
	-v /opt/fj-collector/collector/logs:/collector/logs \
	-v /opt/fj-collector/collector/config:/collector/config \
	-v /opt/fj-collector/collector/keys:/collector/keys \
	--log-opt max-size=10m --log-opt max-file=3 \
	localhost/fj-collector:latest

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


	podman stop graphite
	podman start graphite

	echo "PAUSE BEFORE CHANGE CONFIG (60 secs)"

	sleep 60

	$(MAKE) update_addr
	$(MAKE) update_logins
	$(MAKE) update_datasource
	$(MAKE) update_theme

	podman stop fj-collector
	podman start fj-collector

.ONESHELL:
stop:
	podman stop graphite
	podman stop grafana
	podman stop fj-collector

.ONESHELL:
remove:
	podman rm graphite
	podman image rm docker.io/graphiteapp/graphite-statsd
	podman rm grafana
	podman image rm docker.io/grafana/grafana-enterprise
	podman rm fj-collector
	podman image rm localhost/fj-collector
	podman image rm docker.io/library/debian

.ONESHELL:
start:
	podman start graphite
	podman start grafana
	podman start fj-collector
	podman inspect grafana -f '{{ .NetworkSettings.IPAddress }} {{ .NetworkSettings.Ports }}'
	podman inspect graphite -f '{{ .NetworkSettings.IPAddress }} {{ .NetworkSettings.Ports }}'
	podman inspect fj-collector -f '{{ .NetworkSettings.IPAddress }} {{ .NetworkSettings.Ports }}'

.ONESHELL:
update_addr:
	@$(eval MYVAR=`podman inspect graphite -f '{{ .NetworkSettings.IPAddress }}' 2> /dev/null`)
	echo $(MYVAR)
	if ([ -f /opt/fj-collector/collector/config/config.yaml ] && [[ ! -z $MY_VAR ]])
	then
		sed -i "s/repository\:.*/repository\: $(MYVAR)/" /opt/fj-collector/collector/config/config.yaml
		echo "Updated Config File"
	fi
	@$(eval MYVAR=`podman inspect grafana -f '{{ .NetworkSettings.IPAddress }}' 2> /dev/null`)
	echo $(MYVAR)
	if [ -f /opt/fj-collector/collector/config/config.yaml ] && [[ ! -z $MY_VAR ]]
	then
		sed -i "s/grafana_server\:.*/grafana_server\: $(MYVAR):3000/" /opt/fj-collector/collector/config/config.yaml
		echo "Updated Config File"
	fi


.SILENT:
.ONESHELL:
update_logins:
	@
	MYVAR=$$(podman inspect grafana -f '{{ .NetworkSettings.IPAddress }}' 2> /dev/null)
	echo $$MYVAR
	if [[ ! -z $$MYVAR ]]
	then
		echo "Going to reset admin password"
		@podman exec grafana grafana cli admin reset-admin-password admin
		echo "Going to create service account"
		@RCURL=$$(curl -X POST http://admin:admin@$$MYVAR:3000/api/serviceaccounts -H "Content-Type: application/json" -d '{"name":"fj-collector", "role":"Admin"}' 2>/dev/null | cut -d ":"  -f 2 | cut -d "," -f 1);
		echo $$RCURL
		
		if [[ $$RCURL =~ ^[0-9] ]]
		then
			echo "Will create token"
		    @TCURL=$$(curl -X POST http://admin:admin@$$MYVAR:3000/api/serviceaccounts/$$RCURL/tokens -H "Content-Type: application/json" -d '{"name":"fj-collector"}' 2>/dev/null | cut -d "," -f 3| cut -d ":" -f 2 | tr -d \} | tr -d \");
			echo $$TCURL
			if [ -f /opt/fj-collector/collector/config/config.yaml ] && [[ ! -z $TCURL ]]
			then
				sed -i "s/grafana_api_key\:.*/grafana_api_key\: $$TCURL/" /opt/fj-collector/collector/config/config.yaml
				echo "Updated Config File"
			fi 
		fi

		echo "Reset User and created service account"
	fi

.ONESHELL:
update_theme:
	@
	MYVAR=$$(podman inspect grafana -f '{{ .NetworkSettings.IPAddress }}' 2> /dev/null)
	RCURL=$$(curl -X PUT http://admin:admin@$$MYVAR:3000/api/org/preferences -H "Content-Type: application/json" -d '{ "theme": "light" }' 2>/dev/null)

	if [ "$$RCURL" == "{\"message\":\"Preferences updated\"}" ]
	then
		echo "Light Grafana default theme updated sucessfully"
	else
		echo "Error updating grafana default theme: $$RCURL"
	fi

.ONESHELL:
update_datasource:
	@
	MYVAR=$$(podman inspect grafana -f '{{ .NetworkSettings.IPAddress }}' 2> /dev/null)
	MYGRAPHITE=$$(podman inspect graphite -f '{{ .NetworkSettings.IPAddress }}' 2> /dev/null)

	RCURL=$$(curl -X POST http://admin:admin@$$MYVAR:3000/api/datasources -H "Content-Type: application/json" -d '{ "name":"Graphite", "type":"graphite", "url":"http://'$$MYGRAPHITE'", "access":"proxy", "isdefault":true }' 2>/dev/null)
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
	podman build . -t fj-collector:latest


	podman run -d \
	--name fj-collector \
	--restart=always \
	-v /opt/fj-collector/collector/logs:/collector/logs \
	-v /opt/fj-collector/collector/config:/collector/config \
	-v /opt/fj-collector/collector/keys:/collector/keys \
	--log-opt max-size=10m --log-opt max-file=3 \
	localhost/fj-collector:latest

	rm Dockerfile