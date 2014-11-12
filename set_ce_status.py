######################################################
# set_ce_status.py
# -----------
# Author: Stefanie Langrock
#         <s.langrock@qmul..ac.uk>
#
# Description:
#    Script to update CE status on CouchDB
#
# Can exclude or allow CEs according to the user input 
# from the command line. Extracts a list of all CEs 
# available to snoplus.snolab.ca and compares it to the
# CEs listed in the database. Adds CEs to the database 
# if they are not included.  
# 
######################################################

import os
import couchdb
import getpass

from GangaSNOplus.Lib.Applications import job_tools

def set_ce_permissions(ce_list):

    #access the server using the admin log in
    server = couchdb.Server("http://snoplus.cpp.ualberta.ca:5984")
    username = raw_input("Username for [%s]: " % server)
    password = getpass.getpass("Password for [%s]: " % server)
    server.resource.credentials = (username,password)

    #find the test_grid database
    database = server["test_grid"]

    host_list = []

    #loop over all items in the database
    for id in database:

        #access the document related to id
        document = database[id]

        if id=="_design/ganga":
            continue

        #get the host key (i.e. the CE)
        host = str(document['host'])

        #if the CE given in the host key is not returned by the lcg-infosites command, but it is permitted, exclude CE. If permission status is false, do nothing. 
        if host not in ce_list and document['permit'] == True:
            print "CE %s not found, excluding CE! " % host
            document['permit'] = False
            database[id] = document

        elif host not in ce_list and document['permit'] == False:
            print "CE %s not found, CE not permitted! " % host 
            continue
 
        #go through all the CEs returned by lcg-infosites
        for sites in ce_list:
            if sites == host:
                #ask the user wether CE should be excluded
                prompt = "Exclude CE %s? (y/N): " % host
                result = raw_input(prompt)

                #if yes, change permission status in the document
                if result == 'Y' or result == 'y':
                    print 'Excluding CE: ', host
                    document['permit'] = False
                    database[id] = document

                #if no, check if the permission key is set to True or False. If it is True, do nothing, if it is set to False, change it to True
                elif result == 'N' or result == 'n':
                    if document['permit'] == False:
                        print 'Permitting CE: ', host
                        document['permit'] = True
                        database[id] = document
                    else:
                        print 'No changes made for CE ', host 
                        continue
                    
            if sites != host:
                continue
        #save all CE found in the host key to a list for further use
        host_list.append(host)
  
    #if CE found by lcg-infosites is not in the database, create a new document for it, adding the permission status after asking the user
    for site in ce_list:
        if site not in host_list:
            print 'Adding document for CE %s! ' % site
            prompt = "Exclude CE %s? (y/N): " % site
            result = raw_input(prompt)
        
            if result == 'Y' or result == 'y':
                doc_id, doc_rev = database.save({'host': site, 'permit': False, 'type': 'ce'})

            if result == 'N' or result == 'n':
                doc_id, doc_rev = database.save({'host': site, 'permit': True, 'type': 'ce'})

        else:
            continue

    print "All done!"

if __name__ == '__main__':
    ce_list = []

    #get all CEs from lcg-infosites and safe them in a list
    rtc, out, err = job_tools.execute('lcg-infosites', ['--vo', 'snoplus.snolab.ca', 'ce'])
    for line in out:
        bits = line.split()
        if len(bits)==6:
            ce_name = bits[5]
            ce = ce_name.split(':',1)
            if ce[0] not in ce_list:
                ce_list.append(ce[0])

    #run the function that sets the permissions for each CE
    set_ce_permissions(ce_list)