#!/bin/bash

echo "Installing OASIS service"

echo "Please specify the instance that you'd like to install: "
echo "-------------------------------------------------------------------------"
echo "itb:                ITB Stratum 0 server"
echo "prod:                    Production Stratum 0 server"
echo "-------------------------------------------------------------------------"
echo -n "Please Select: "
read -e type
case $type in
    itb)
            export INSTALL_HOSTNAME=oasis-itb.grid.iu.edu
            export PUPPET_ENV=itb
            ;;
    prod)
            export INSTALL_HOSTNAME=oasis.grid.iu.edu
            export PUPPET_ENV=prod
            ;;
    *)
            echo 'Invalid Instance Type!'
            exit 1
            ;;
esac

export INSTALL_IPTABLE_RULE=files/60-local-service-rules

source "../common/setup_network.sh"
source "../common/setup_usercert.sh"
source "../common/force_sync.sh"
source "../common/setup_ssh_keys.sh"
"../common/setup_puppet.sh" $PUPPET_ENV


case $type in
    itb)
	reponame="oasis-itb.opensciencegrid.org"
	mkdir /srv
	;;
    prod)
	reponame="oasis.opensciencegrid.org"
## mount the previously made disk image
	echo "This virtual machine must be built in a special way:"
	echo " "
	cat files/vm-build.instructions
	echo " "
	echo -n "Was the machine built this way? [y/n]: "
	read -e answer
	case $answer in
	    y)
		echo "Proceeding"
		;;
	    n)
		echo "Build cannot continue"
		echo "Please save and follow the above instructions and try again"
		exit
		;;
	esac
	echo -e "LABEL=/srv\t/srv\text4\tdefaults\t1 2" >> /etc/fstab
	mount /srv
	;;
    *)
	echo 'Invalid Instance Type!'
	exit 1
	;;
esac



echo "installing epel & yum-priorities & osg-release"
rpm -Uvh http://dl.fedoraproject.org/pub/epel/5/i386/epel-release-5-4.noarch.rpm
yum -y install yum-priorities
rpm -Uvh http://repo.grid.iu.edu/osg-el5-release-latest.rpm

echo "installing rpms"
yum -y install httpd pwgen mod_ssl

echo "installing oasis scripts"
cp -r files/oasis /usr/local/

BASEDIR=`pwd`

mkdir -p /etc/pki/rpm-gpg/
cp files/RPM-GPG-KEY-CernVM /etc/pki/rpm-gpg/RPM-GPG-KEY-CernVM

cd /etc/yum.repos.d
wget http://cvmrepo.web.cern.ch/cvmrepo/yum/cernvm.repo
cd -

### the cvmrepo has a bug, fix it here
ver=`rpm -q redhat-release | awk -F- '{print $4}' | awk -F. '{print $1"."$2}'`
sed s/\$releasever/$ver/ <cernvm.repo >aaa
arch=`uname -i`
sed s/\$basearch/$arch/ <aaa >cernvm.repo
rm -f aaa

### condor has an unresolved dependency, fix it
wget "http://rpmfind.net/linux/rpm2html/search.php?query=gsoap/gsoap-2.7.13-4.el5.x86_64.rpm" >/tmp/gsoap-2.7.13-4.el5.x86_64.rpm
rpm -i /tmp/gsoap-2.7.13-4.el5.x86_64.rpm
rm -f /tmp/gsoap-2.7.13-4.el5.x86_64.rpm

### load the kernel modules
yum -y install redirfs kmod-redirfs cvmfsflt kmod-cvmfsflt
modprobe redirfs && modprobe cvmfsflt

### make directories needed by cvmfs on the shared filesystem

### install the service
yum -y --nogpgcheck install cvmfs-release.noarch
yum -y install cvmfs-server cvmfs-keys
yum -y install condor

### for logging
mkdir -p /var/log/oasis

### globus stuff
#yum -y install globus-gridftp globus-gram5
#yum -y install globus-gridftp-server-progs globus-gass-copy-progs myproxy myproxy-server myproxy-admin globus-simple-ca globus-gss-assist-p gs

### the habd maintained grid-mapfile, will need to come from files during install
#grid-mapfile-add-entry -dn "/DC=org/DC=doegrids/OU=People/CN=Scott Teige 689374" -ln steige

### set the services to start on boot
chkconfig --levels 345 condor on
chkconfig --levels 2345 cvmfsd on

### cleanup some un-needed files from install
cd /etc/cvmfs
rm -f replica.conf
cp -f server.conf server.local
cd -

### may need to remove any pre-existing repositories, depending on how we get content
cvmfs_server mkfs $reponame
touch /srv/cvmfs/$reponame/pub/catalogs/.cvmfs_master_replica

### get a file that contains the information needed for a replica (stratum 1 server) to use this server
replica_info_file="/root/replica.info"
cvmfs_server info > $replica_info_file
echo " " >> $replica_info_file
cat /etc/cvmfs/keys/$reponame.pub >> $replica_info_file

cp -f $BASEDIR/files/$INSTALL_HOSTNAME/replica.info /root/replica.info

### condor configuration (moved to /etc/backup.conf)
#echo "START_LOCAL_UNIVERSE = TotalLocalJobsRunning < 1" >> /etc/condor/condor_config

echo "Installing AWStat"
wget http://prdownloads.sourceforge.net/awstats/awstats-7.1.1.tar.gz
tar -xzf awstats-7.1.1.tar.gz -C /usr/local
ln -s /usr/local/awstats-7.1.1 /usr/local/awstats
chown apache:apache -R /usr/local/awstats-7.1.1
chmod +x /usr/local/awstats/wwwroot/cgi-bin/*.pl
chmod +x /usr/local/awstats/tools/*.pl

####################################################################
#
echo "restoring softback-up files"
../common/restore.py
echo "10 */6 * * * root /root/install/common/backup.py" > /etc/cron.d/backup
#
####################################################################

### start up the services
service httpd restart
/sbin/chkconfig --add httpd
/sbin/chkconfig --levels 345 httpd on
service condor start
service cvmfsd start

case $type in
    itb)
	echo "Skipping key overwrite"
	;;
    prod)
### overwrite the keys written by this install
	cp -f $BASEDIR/files/$INSTALL_HOSTNAME/cvmfs-keys/* /etc/cvmfs/keys

### get content from backup
	scp -q -r -i /root/.ssh/id_goc.dsa goc@backup.goc:/usr/local/backup/oasis/cvmfs/oasis.opensciencegrid.org/* /cvmfs/oasis.opensciencegrid.org/
	;;
    *)
	echo 'Invalid Instance Type!'
	exit 1
	;;
esac

### sym link to make cern cvmfs visible 
mkdir /cvmfs/$reponame/cmssoft
ln -s /cvmfs/cms.cern.ch /cvmfs/$reponame/cmssoft/cms

cvmfs-sync
cvmfs_server publish

### because we used previous keys (does not hurt on itb)
cvmfs_server resign

echo "all done"

