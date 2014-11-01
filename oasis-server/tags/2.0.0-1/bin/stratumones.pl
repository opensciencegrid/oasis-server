#!/usr/bin/perl -w

use strict;
use LWP::Simple;
use Date::Format ;
use Getopt::Std;
our ($opt_r);
getopts('r:') ;
my $vo = $opt_r;

my $nowstr = time2str("%Y-%m-%d %X",time);
print STDERR "\n$nowstr: $vo\n";

# Number of revisions and time in seconds that a stratum one may fall behind a stratum 0.
our $seqoffset  = 8 ;

our $timeoffset = 10800;   # 3 hours
our %repo;

my $zero = "cvmfs-stratum-zero.cern.ch";
my @ones = ("cvmfs-stratum-one.cern.ch", "cernvmfs.gridpp.rl.ac.uk", "cvmfs.racf.bnl.gov", 
            "cvmfs.fnal.gov","cvmfs02.grid.sinica.edu.tw");


my ($zstamp,$zseq) =  &getrepoinfo($zero,$vo) ;

my $avail = 100 ;

foreach (@ones)  {
  my ($stamp,$seq) = &getrepoinfo($_,$vo);

  my ($unavail,$unavailinfo) = &getavail($stamp,$seq,$zstamp,$zseq,$_) ;
  print STDERR "$unavailinfo\n" if $unavailinfo ;
  $repo{$_}{'stamp'} =  $stamp ;
  $repo{$_}{'seq'}   =  $seq ;
  $repo{$_}{'unavail'} =  $unavail;
  $repo{$_}{'unavailinfo'} =  $unavailinfo;
  $avail = $avail - $unavail;

}

$avail = 0 if $avail < 0 ;

&outputXML();


sub outputXML()  {
  print  '<?xml version="1.0" encoding="utf-8"?>'."\n";
  print  '<serviceupdate xmlns="http://sls.cern.ch/SLS/XML/update">'."\n"; 
  print  "<id>CVMFS_Stratum1_${vo}</id>\n";
  print  "<fullname>Stratum One Service for ${vo}.cern.ch CVMFS Repository</fullname>\n" ;
  print  "<group>IT/PES</group>\n";

  print  <<"EOF";
<availabilitythresholds>
                <threshold level="available">90</threshold>
                <threshold level="affected">70</threshold>
                <threshold level="degraded">40</threshold>
</availabilitythresholds>
EOF

  print  "<availabilitydesc>\n" ;
  print  <<"EOF";
  The CVMFS stratum one service for repository ${vo}.cern.ch is 100% available if 
       three conditions are met:\%BR\% 
  (1) Either the stratum zero catalogue timestamp has been updated in the
      last $timeoffset seconds, or all the stratum one catalogue timestamps
      exactly match the stratum one timestamp.\%BR\%
  (2) The catalogue release sequence number for each stratum one is at most
      $seqoffset releases behind the stratum zero sequence number.\%BR\%
  (3) All the stratum ones can be queried to find their catalogue release
      timestamp and sequence number.

EOF
  print  "</availabilitydesc>\n" ;
  print  "<notes>\n" ;
  print  "Stratum 0: ${zero}\%BR\%\n" ;
  print  "http://${zero}/opt/${vo}/.cvmfspublished \%BR\%\n" ;
  print  "Catalog epoch: $zstamp \%BR\%\n" ;
  print  "Catalog time: ".time2str( "%Y-%m-%d %X", $zstamp )." \%BR\%\n" ;
  print  "Catalog sequence: $zseq.\%BR\%\n" ; 
  print  "\%BR\%\n";
  foreach (sort keys %repo) {
    print  "Stratum 1: $_\%BR\%\n";
    print  "http://$_/opt/${vo}/.cvmfspublished \%BR\%\n";
    print  "Catalog epoch: ".$repo{$_}{'stamp'}."\%BR\%\n" ;
    print  "Catalog time: ".time2str("%Y-%m-%d %X",$repo{$_}{'stamp'})."\%BR\%\n" ;
    print  "Catalog sequence ".$repo{$_}{'seq'}.".\%BR\%\n" ;
    print  "\%BR\%\n";
  }
  print  "</notes>\n" ;
  print  "<availabilityinfo>\n" ;
  foreach (sort keys %repo) {
     print $repo{$_}{'unavailinfo'}.'%BR%'.".\n" if $repo{$_}{'unavailinfo'};
  }
  print  "</availabilityinfo>\n" ;

  print  "<availability>$avail</availability>\n" ;
  print  "<timestamp>".time2str( "%Y-%m-%dT%X", time )."</timestamp>\n";
  print  "<validityduration>PT1H</validityduration>\n" ;
  print  "<refreshperiod>PT15M</refreshperiod>\n" ;
  print "</serviceupdate>\n" ;

}



#fully available if its availability X is: 90 <= X <= 100
#affected if its availability X is: 70 <= X < 90
#degraded if its availability X is: 40 <= X < 70
#not available if its availability X is: 0 <= X < 40


sub getavail() {
  my ($stamp,$seq,$zstamp,$zseq,$host) = @_ ;
  my $unavail = 0 ;
  my $now = time;
  # Check if we just can't parse the file basically for whatever reason.
  # This is not as bad, just affected.
  if ( $stamp == -1 || $seq == -1 ) {
     return (20,"Stratum 1 on $host is down: -20% availability")  ;
  }

  # First check for the worse problem of being out of time sync.
  # For even one host this is bad and we are degraded.
  # Repositories are only intermittently updated and then a stratum 1
  #    can suddenly appear very old, so only check time if the stratum 0
  #    0 hasn't been updated for a while.
  if ( $now - $zstamp >= $timeoffset && $zstamp != $stamp) {
     my $diff = $now - $stamp;
     my $seqdiff = $zseq - $seq ;
     return (35, "Stratum 1 on $host has not been updated for $diff seconds and is $seqdiff releases behind : -35% availability")   ;
  }
  # Check if the revisions on a strat1 are too far behind the 
  # stratum zero, this is also pretty bad.
  if ( $seq + $seqoffset <= $zseq ) {
     my $diff = $zseq - $seq ;
     my $timediff = $now - $stamp;
     return (35, "Stratum 1 on $host is $diff releases behind and has not been updated for $timediff seconds: -35% availability") ;
  }
  # Now the much lesser problems which just prints info so we see it.
  if ( $stamp != $zstamp ) {
     my $diff = $now - $stamp;
     my $seqdiff = $zseq - $seq ;
     return (0, "Stratum 1 on $host is slightly behind the stratum zero by $seqdiff releases and has not been updated for $diff seconds: info only")   ;
  }



  return $unavail;
}
sub getrepoinfo() {
  my ($host,$vo) = @_;
  my $time = -1 ;
  my $seq = -1 ;
  my $url = "http://${host}/opt/${vo}/.cvmfspublished" ;
  my $content = get($url);
  if ($content) {
     $seq = $1 if  $content =~ m/.*^S(\d+)$/m ;
     $time = $1 if  $content =~ m/.*^T(\d+)$/m ;
  }
  return ($time,$seq)
}
