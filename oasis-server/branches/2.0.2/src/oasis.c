#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>


/* 
    NOTE:

    a better version of this code 
    to switch ID and restore back
    can be found here
    
    http://www.gnu.org/software/libc/manual/html_node/Setuid-Program-Example.html
*/


int main (void)
{

    /* Remember the effective and real UIDs. */
    static uid_t euid, ruid;
    ruid = getuid ();
    euid = geteuid ();

    int rc;
 
    rc = system("/usr/bin/oasis --oasiscmd=runprobes");
    if (rc == 0){
        /* change ID  */
        setreuid(geteuid(), getuid());
        system("/usr/bin/oasis --oasiscmd=publish");
        /* restore ID  */
        setreuid(ruid, euid); 
    }
}


