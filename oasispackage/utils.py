import commands

def adduser(user):
    '''
    creates the UNIX ID
    '''

    uid = _checkuser(user)
    if uid:
        #self.log.warning('user %s already exists' %user)
        return 0
    else:
        group = user  # maybe in the future is a generic group name like 'oasis'?

        # FIXME: what about the group?? 
        # option -g in adduser requires the group to exist !!
        # or we put all users in the same group... 
        cmd = '/usr/sbin/adduser -m %s' %user
        rc, out = commands.getstatusoutput(cmd)

        #if rc == 0:
        #    self.log.debug('user %s created' %user)
        #else:
        #    self.log.critical('user %s creation failed' %user)

        return rc


def _checkuser(user):
    '''
    checks if that username already exists
    '''
    # FIXME is this really needed?

    try:
        pw = pwd.getpwnam(user)
        return pw.pw_uid
    except:
        return None




