# create SP J2C Auth entries
# note: Did not use AdminTask.createAuthDataEntry for this as it will respect the "prefix check box" 
#   and we can't tell if it's checked or not from here, so we'd not know the resulting name for sure

'''
hmm, there is this:
AdminTask.setAdminActiveSecuritySettings('[-customProperties["com.ibm.websphere.security.JAASAuthData.removeNodeNameGlobal=true"]]')
(true means the checkbox is not checked, so prefix will not automatically be added)

AdminTask.createAuthDataEntry('[-alias "DbAuthTest3" -user millarde -password TopSecret]')

AdminTask.modifyAuthDataEntry('[-alias "ADMINIB-3OAPBALNode01/DbAuthTest3" -user millard3 -password NewerSecret]')

TODO: Consider changing to use AdminTask and then add a "ChangeJ2CPassword" feature so users can update the password
'''

import os

# clear checkbox -- this is for backwards compatibility with things we don't have
AdminTask.setAdminActiveSecuritySettings('[-customProperties["com.ibm.websphere.security.JAASAuthData.removeNodeNameGlobal=true"]]')

userid08b = os.environ["MY_SP_ID_08"]
password08b = os.environ["MY_SP_PASSWORD_08"]
alias08b = 'DbAuth08b'
args = '[-alias "%s" -user %s -password %s]' % (alias08b, userid08b, password08b)
AdminTask.createAuthDataEntry(args)


userid23b = os.environ["MY_SP_ID_23"]
password23b = os.environ["MY_SP_PASSWORD_23"]
alias23b = 'DbAuth23b'
args = '[-alias "%s" -user %s -password %s]' % (alias23b, userid23b, password23b)
AdminTask.createAuthDataEntry(args)


AdminConfig.save()
print "JAAS/J2C settings updated"
