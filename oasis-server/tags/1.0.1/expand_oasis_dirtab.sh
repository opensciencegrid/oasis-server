#!/bin/bash

# This is adapted from cvmfs-sync command from cvmfs-server 2.0

. /etc/cvmfs/server.conf
if [ -f /etc/cvmfs/server.local ]; then
  . /etc/cvmfs/server.local
fi

for reqvar in SHADOW_DIR
do
   eval value=\$$reqvar
   if [ -z "$value" ]; then
      echo "Set a value for $reqvar in /etc/cvmfs/server.local"
      exit 1
   fi
done

if [ -f "$SHADOW_DIR/.oasisdirtab" ]; then
   echo "Auto-creating nested catalogs..."
   cd /tmp # move to any readable directory so find won't complain
   EXCLUDES=""
   if [ -f "$SHADOW_DIR/.oasisdirexclude" ]; then
     IFS=$'\n' EXCLUDES=($(< $SHADOW_DIR/.oasisdirexclude)) 
   fi
   for d in `cat "$SHADOW_DIR/.oasisdirtab"`
   do
      GOTERROR=false
      for subdir in ${SHADOW_DIR}$d; do
         if [ ! -r "$subdir" ]; then
            echo "ERROR: cannot read $subdir" >&2
            GOTERROR=true
            break
         fi
      done
      if $GOTERROR; then
         continue
      fi
      for subdir in `find ${SHADOW_DIR}$d -maxdepth 1 -mindepth 1 -type d`
      do
         EXCLUDED=false
         for x in "${EXCLUDES[@]}"; do
            if [[ $subdir == $x ]]; then
               EXCLUDED=true
               break
            fi
         done
         if $EXCLUDED; then continue; fi
         if [ `basename $subdir | head -c 1` != "." ]; then
           if [ ! -f "$subdir/.cvmfscatalog" ]; then
             echo "Auto-creating nested catalog in $subdir"
             touch "$subdir/.cvmfscatalog" 
           fi
         fi  
      done
   done
fi

