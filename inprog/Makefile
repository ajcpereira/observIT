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
	
.ONESHELL:
setup:
	podman pull docker.io/graphiteapp/graphite-statsd
	podman pull docker.io/grafana/grafana-enterprise
	mkdir -p /opt/fj-collector
	cd /opt/fj-collector
	#mkdir repo
	#cd repo
	#git clone https://github.com/ajcpereira/fj-collector.git
	#cd fj-collector
	#--log-driver json-file --log-opt max-size=10m --log-opt max-file=3
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
    --restart=unless-stopped \
    -p 3000:3000/tcp \
    -v /opt/fj-collector/grafana/provisioning/:/etc/grafana/provisioning/ \
    -v /opt/fj-collector/grafana/data/grafana:/var/lib/grafana/ \
    -u 0 \
	--log-opt max-size=10m --log-opt max-file=3 \
	grafana/grafana-enterprise
	

.ONESHELL:
stop:
	podman stop graphite
	podman stop grafana-enterprise

.ONESHELL:
remove:
	podman rm graphite
	podman image rm docker.io/graphiteapp/graphite-statsd
	podman rm grafana
	podman image rm docker.io/grafana/grafana-enterprise

.ONESHELL:
start:
	podman start graphite
	podman start grafana
	sudo podman inspect grafana -f '{{ .NetworkSettings.IPAddress }} {{ .NetworkSettings.Ports }}'
	sudo podman inspect graphite -f '{{ .NetworkSettings.IPAddress }} {{ .NetworkSettings.Ports }}'