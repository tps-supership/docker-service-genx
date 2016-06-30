#!/usr/bin/env python
from subprocess import Popen, PIPE
import json
import os
from string import Template



path = 'docker'

host_ip = os.getenv('HOST_IP','arcariuscreate.net')


template = Template('''server {
    gzip_types text/plain text/css application/json application/x-javascript text/xml application/xml application/xml+rss text/javascript;

    server_name $SERVER_NAME;
    proxy_buffering off;
    error_log /proc/self/fd/2;
    access_log /proc/self/fd/1;

    location / {
        proxy_pass http://$HOST_IP:$SERVICE_PORT;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # HTTP 1.1 support
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
''')

file_path = '/etc/nginx/sites-enabled'



def _run(cmd, raise_error=True):
    cmd = [path] + cmd

    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    error_code = p.returncode
    if raise_error and error_code:
        raise RuntimeError("cmd returned error %s: %s" % (error_code, stderr.decode('utf-8').strip()))
    return stdout.decode('utf-8'), stderr.decode('utf-8'), error_code


def service_ls():
    cmd = ['service', 'ls', '-q']
    stdout, stderr, errorcode = _run(cmd)
    return stdout.strip().split('\n')


def get_port_description(service_id):
    cmd = ['service', 'inspect', service_id, '-f', '{"host": {{json .Spec.Labels}}, "port": {{json .Spec.EndpointSpec.Ports}}}']
    stdout, stderr, errorcode = _run(cmd)
    obj = json.loads(stdout.strip())
    if obj:
        if obj[u'host'] is None:
            return None
        if obj[u'port'] is None:
            return None
        return obj
    return None

def build_template(port_description):
    subdomain = str(port_description[u'host'][u'vhost'])
    port = port_description[u'port'][0][u'PublishedPort']
    node = template.safe_substitute( SERVER_NAME=subdomain,
                                HOST_IP=host_ip, 
                                SERVICE_PORT=port ) 
    return node

def create_config(services):
    config = ""
    for service_id in services:
        ports = get_port_description(service_id)
        if ports:
            config += build_template(ports)
    return config


def save(config):
    with open(file_path + '/reverse_proxy', 'w') as f:
        f.write( config )

def update():
    cmd = ['exec', 'nginx', 'nginx', '-s', 'reload']
    stdout, stderr, errorcode = _run(cmd)
    print(stdout)

def run():
    config = create_config( service_ls() )
    save(config)
    update()


if __name__ == "__main__":
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    run()
