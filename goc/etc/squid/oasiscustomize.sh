#!/bin/bash

awk --file `dirname $0`/customhelps.awk --source '{

# cache only api calls
insertline("^http_access deny all", "acl CVMFSAPI urlpath_regex ^/cvmfs/[^/]*/api/")
insertline("^http_access deny all", "cache deny !CVMFSAPI")

# port 80 is also supported, through an iptables redirect
setoption("http_port", "8000 accel defaultsite=localhost:8081 no-vhost")
setoption("cache_peer", "localhost parent 8081 0 no-query originserver")
# listen on additional port for Cloudflare CDN
insertline("^(# |)http_port", "http_port 8080 accel defaultsite=127.0.0.1:8081 no-vhost")

# allow incoming http accesses from anywhere
# all requests will be forwarded to the originserver
commentout("http_access allow NET_LOCAL")
insertline("^http_access deny all", "http_access allow all")

# do not let squid cache DNS entries more than 5 minutes
setoption("positive_dns_ttl", "5 minutes")
# set shutdown_lifetime to 0 to avoid giving new connections error 
# codes, which get cached upstream
setoption("shutdown_lifetime", "0 seconds")

# turn off collapsed_forwarding to prevent slow clients from slowing down faster ones
setoption("collapsed_forwarding", "off")

print
}'
