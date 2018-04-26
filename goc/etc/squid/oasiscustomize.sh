
WORKERS=3
SERVICES=${SQUID_NUM_SERVICES:-1}
HOSTNAME=`hostname`

awk --file `dirname $0`/customhelps.awk --source '{

# cache only api calls
insertline("^http_access deny all", "acl CVMFSAPI urlpath_regex ^/cvmfs/[^/]*/api/")
insertline("^http_access deny all", "cache deny !CVMFSAPI")

# port 80 is also supported, through an iptables redirect to port 8000
if ($1 == "http_port") {
    $0 = "# " $0
    for (n = 0; n < '$SERVICES'; n++ ) {
	if (n > 0)
	    print "else"
        print "if ${service_name} = " n
	squidport = 8000 + n
	apacheport = 8081 + n
	print "http_port " squidport " accel defaultsite=localhost:" apacheport " no-vhost"
	if (n == 0) {
	    # extra port for Cloudflare
	    print "http_port 8080 accel defaultsite=localhost:" apacheport " no-vhost"
	}
	print "cache_peer localhost parent " apacheport " 0 no-query originserver"
    }
    for (n = 0; n < '$SERVICES'; n++ ) {
	print "endif"
    }
}

# configure multiple workers for multiple services
setoption("workers", '$WORKERS')
setoptionparameter("cache_dir", 2, "/var/cache/squid/squid${service_name}-${process_number}")
setoptionparameter("cache_dir", 3, "100")
setoptionparameter("access_log", 1, "daemon:/var/log/squid/squid${service_name}/access.log")
setoption("cache_log", "/var/log/squid/squid${service_name}/cache.log")
setoption("pid_filename", "/var/run/squid/squid${service_name}.pid")
setoptionparameter("logformat awstats", 3, "kid${process_number}")
setoption("visible_hostname", "'$HOSTNAME'/${service_name}-${process_number}")
setserviceoption("snmp_port", "", 3401, '$SERVICES', 1)
# the number of cores in the lists should be at least as much as $WORKERS
setserviceoption("cpu_affinity_map", "process_numbers=1,2,3 cores=", "2,3,4", '$SERVICES', '$WORKERS')

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
