#!/usr/bin/env python 

#
# a command like this
#
#       $ ldapsearch -LLL -h is.grid.iu.edu -p 2170 -x -b 'o=grid' '(&(objectClass=GlueCE)(GlueCEAccessControlBaseRule=VO:atlas))' \
#           GlueCEInfoHostName GlueCEInfoGatekeeperPort GlueCEInfoJobManager GlueCEImplementationName
#
# gives a lot of blocks like this 
#
#                dn: GlueCEUniqueID=antaeus.hpcc.ttu.edu:2119/jobmanager-sge-ivy-highmem,Mds-Vo
#                 -name=TTU-ANTAEUS,Mds-Vo-name=local,o=grid
#                GlueCEImplementationName: Globus
#                GlueCEInfoHostName: antaeus.hpcc.ttu.edu
#                GlueCEInfoGatekeeperPort: 2119
#                GlueCEInfoJobManager: sge
#
# they need to be converted into something like 
#
#                [ANALY_BNL_MCORE-gridgk03]
#                batchqueue = ANALY_BNL_MCORE-condor
#                wmsqueue = ANALY_BNL_MCORE
#                batchsubmit.condorgt5.gridresource = gridgk03.racf.bnl.gov/jobmanager-condor
#                globusrsl.gram5.queue = amc
#                executable.arguments = %(executable.defaultarguments)s -u user
#


ldap = open('/tmp/ldap')   # /tmp/ldap is the file with the output of the ldapsearch command

class CE(object):
    def __init__(self):
        pass

list_ce = []

for line in ldap.readlines():
        line = line.strip()
            if "GlueCEUniqueID" in line:
                new_ce = CE()
            elif "-name" in line:
                new_ce.Name = line.split('=')[1].split(',')[0]
            elif "GlueCEImplementationName" in line:
                new_ce.GlueCEImplementationName = line.split()[-1]
            elif "GlueCEInfoHostName" in line:
                new_ce.GlueCEInfoHostName = line.split()[-1]
            elif "GlueCEInfoGatekeeperPort" in line:
                new_ce.GlueCEInfoGatekeeperPort = line.split()[-1]
            elif "GlueCEInfoJobManager" in line:
                new_ce.GlueCEInfoJobManager = line.split()[-1]
                list_ce.append(new_ce)
            else:
                pass


for ce in list_ce:
        print "[%s]" %ce.Name
        if ce.GlueCEImplementationName == "Globus":
            print "batchsubmitplugin = CondorGT5"
            print "batchsubmit.condorgt5.gridresource = %s/jobmanager-%s" %(ce.GlueCEInfoHostName, ce.GlueCEInfoJobManager)
        if ce.GlueCEImplementationName == "HTCondorCE":
            print "batchsubmitplugin = CondorOSGCE"
            print "batchsubmit.condorosgce.gridresource = %s" ce.GlueCEInfoHostName
        
        

            


