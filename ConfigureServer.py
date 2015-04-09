# All steps for configuring an SPNG Backend server (except for the JAAS J2C Authentication entries which require a save and server restart to take effect)
import os

myServerName = os.environ["WAS_PROFILE_SERVER_NAME"]
myNodeName = os.environ["MY_WAS_NODE"]
myCellName = myNodeName+"Cell"

doneMarker = "#"

def createJDBCProvider():
    providerName = "DB2 Universal JDBC Driver Provider (XA)"
    print "Checking for JDBC Provider " + providerName

    # Test to see if the provider has already been created.
    jdbcdb2provider = AdminConfig.getid("/JDBCProvider:" + providerName + "/")
    if len(jdbcdb2provider) == 0:
        print 'Creating %s on %s' % (providerName, myServerName)
    
        args = '[-scope Server='+myServerName+' -databaseType DB2 -providerType "DB2 Universal JDBC Driver Provider" \
    -implementationType "XA data source" -name "DB2 Universal JDBC Driver Provider (XA)" \
    -description "XA DB2 Universal JDBC Driver-compliant Provider. Datasources created under this provider support the use of XA to perform 2-phase commit processing." \
    -classpath "${DB2UNIVERSAL_JDBC_DRIVER_PATH}/db2jcc.jar;${UNIVERSAL_JDBC_DRIVER_PATH}/db2jcc_license_cu.jar;${DB2UNIVERSAL_JDBC_DRIVER_PATH}/db2jcc_license_cisuz.jar" \
    -nativePath "${DB2UNIVERSAL_JDBC_DRIVER_NATIVEPATH}"]'
            
        AdminTask.createJDBCProvider(args)
        
    else:
        print 'DB2 provider already exists, not created.'
    
    #that won't all work without setting up the websphere variables for the DB2UNIVERSAL* items
    print "updating DB2UNIVERSAL* variables"
    
    myDbPath = os.environ["DATABASE_PATH"]
    myDriverPath = myDbPath+"/java"
    myNativePath = myDbPath+"/lib"
    driverPathVarName = "DB2UNIVERSAL_JDBC_DRIVER_PATH"
    nativePathVarName = "DB2UNIVERSAL_JDBC_DRIVER_NATIVEPATH"
    
    AdminTask.setVariable('[ -scope Server='+myServerName+' -variableName '+driverPathVarName+' -variableValue "'+myDriverPath+'"]')
    AdminTask.setVariable('[ -scope Server='+myServerName+' -variableName '+nativePathVarName+' -variableValue "'+myNativePath+'"]')
    print doneMarker

#enddef createJDBCProvider


def createDataSources(): 
    print "Creating data sources..."
    
    def createDataSource(server, provider, providerName, dataSourceName, dsJNDIName, cmaAlias, dbServerName, dbPortNum, dbName) :
        # check to see if the datasource already exists
        dataSource = AdminConfig.getid("/Server:"+server+"/JDBCProvider:"+providerName+"/DataSource:"+dataSourceName+"/")
        if len(dataSource) == 0:
            print "Creating datasource %s" % (dataSourceName)
            # Set the datasource attributes
    
            args = ('[-name %s -jndiName %s -dataStoreHelperClassName com.ibm.websphere.rsadapter.DB2UniversalDataStoreHelper \
        -containerManagedPersistence true -componentManagedAuthenticationAlias "%s" -xaRecoveryAuthAlias "%s" \
        -configureResourceProperties [[databaseName java.lang.String %s][driverType java.lang.Integer 4] \
        [serverName java.lang.String %s][portNumber java.lang.Integer %s]]]') \
        % (dataSourceName, dsJNDIName, cmaAlias, cmaAlias, dbName, dbServerName, dbPortNum)
    
            dataSource = AdminTask.createDatasource(provider, args)
    
        else:
            print "Datasource %s already exists, no changes" % (dataSourceName)
    
        return
    #enddef    

    server08 = "rslaix08b.dub.usoh.ibm.com"
    auth08 = "DbAuth08b"
    server23 = "wccaix23b.dub.usoh.ibm.com"
    auth23 = "DbAuth23b"
    providerName = "DB2 Universal JDBC Driver Provider (XA)"
    
    #fortunately, this doesn't have to have been saved before you can retrieve it
    db2provider = AdminConfig.getid('/Server:'+myServerName+'/JDBCProvider:'+providerName+'/')
    if len(db2provider) == 0:
        raise Exception("Required provider %s does not exist! Abandoning..." % (providerName))
        
    # createDataSource(server, provider, providerName, dataSourceName, dsJNDIName, cmaAlias, dbServerName, dbPortNum, dbName) :
        
    createDataSource(myServerName, db2provider, providerName, "GcsDB", "jdbc/GcsDB", auth08, server08, 50030, "GCS1")  
    createDataSource(myServerName, db2provider, providerName, "QuestDB", "jdbc/QuestDB", auth23, server23, 50002, "SYSSUPT")  
    createDataSource(myServerName, db2provider, providerName, "SCSIDB", "jdbc/SCSIDB", auth23, server23, 50000, "SCSI")  
    createDataSource(myServerName, db2provider, providerName, "SPEDB", "jdbc/SPEDB", auth08, server08, 50030, "SPE")  
    createDataSource(myServerName, db2provider, providerName, "SPE_CST", "jdbc/SPEDB_CST_Editor", auth23, server23, 50000, "SPE")  
    createDataSource(myServerName, db2provider, providerName, "SPE_TILT", "jdbc/SPEDB_TILT", auth23, server23, 50000, "SPE")  

    print doneMarker
#enddef createDataSources


def applySSLCerts():
    print "installing SSL Certs"
    cwd = os.getcwd()
    ssldir=cwd+"/sslcerts"
    files = os.listdir(ssldir)
    
    for aFile in files:
        alias, fileExtension = os.path.splitext(aFile)
        args = '[-keyStoreName NodeDefaultTrustStore -keyStoreScope (cell):%s:(node):%s -certificateFilePath "%s/%s" -base64Encoded true -certificateAlias "%s"]' \
            % (myCellName, myNodeName, ssldir, aFile, alias)
        AdminTask.addSignerCertificate(args) 
        print "SSL certificate added for " + aFile

    print doneMarker
#enddef applySSLCerts


def createServletCaches():
    print "creating servlet caches"
    myServerPath = '/Server:'+myServerName+'/'
    s1 = AdminConfig.getid(myServerPath)
    
    # setup checkbox to enable servlet caching
    wc = AdminConfig.list('WebContainer', s1)
    serEnable = [['enableServletCaching', 'true']]
    AdminConfig.modify(wc, serEnable)
    
    cp = AdminConfig.list('CacheProvider', s1)
    
    # currently, we use name as jndi name, so just define name once and desired size (I'd suggest a dictionary for these if we add jndi name as different)
    # sigh: AdminTask.createServletCacheInstance is not capable of taking a size argument. If we really need this, we'll need to find another way.
    # size setting will be ignored for now
    caches = [
    ("hw-quest-cache", 2000), 
    ("icons-content-cache", 2000),
    ("lookahead", 2000),
    ("quick-subscribe-cache", 2000),
    ("scsi-webidentity-cache", 2000),
    ("search-content-cache", 2000),
    ]
    
    for cache in caches:
        print "Creating servlet cache %s" % (cache[0])
        args = "[-name %s -jndiName %s]" % (cache[0], cache[0])
        AdminTask.createServletCacheInstance(cp, args)

    print doneMarker
#enddef createServletCaches


def createWorkManagers(): 
    print "creating work managers"
    server = AdminConfig.getid('/Server:'+myServerName+'/WorkManagerProvider:WorkManagerProvider/')
    
    # work managers to create (use Python dict to make values clear and easier to update/change)
    # unless you want to change defaults, only first line needs updating. Some less common attributes left out.
    workmanagers = [
    {"name":"scsi.entitlements.provider", "jndiName":"wm/entitlements-provider", "description":"SCSI entitlements provider work manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
            
    {"name":"common.search.work.manager", "jndiName":"wm/cs", "description":"Common Search Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    
    {"name":"chat.service.work.manager", "jndiName":"wm/chat", "description":"Chat Service Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    
    {"name":"seb.service.work.manager", "jndiName":"wm/sebwebservice", "description":"SEB Web Service Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    
    {"name":"bookmark.work.manager", "jndiName":"wm/bookmark", "description":"Bookmarks Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    
    {"name":"nfluentStat.work.manager", "jndiName":"wm/nfluentStat", "description":"nFluent Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    
    {"name":"social.media.data.work.manager", "jndiName":"wm/social_media_data", "description":"Social Media Data Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    
    {"name":"shortcut.links.work.manager", "jndiName":"wm/shortcut_links", "description":"Shortcuts Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    
    {"name":"client.side.tools.work.manager", "jndiName":"wm/client_side_tools", "description":"Client Side Tools Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    
    {"name":"ecc.upload.command.work.manager", "jndiName":"wm/ecc_upload", "description":"ECC upload service Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    
    {"name":"productContext.provider.work.manager", "jndiName":"wm/product_context_provider", "description":"Product Context Provider Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    
    {"name":"contract.data.provider.work.manager", "jndiName":"wm/contract_data_provider", "description":"Contract Data Provider Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    
    {"name":"consolidatedInventory.provider.work.manager", "jndiName":"wm/consolidated_inventory_provider", "description":"Consolidated Inventory Data Provider Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    
    {"name":"notificationSubscriptions.provider.work.manager", "jndiName":"wm/notification_subscriptions_provider", "description":"Notification Subscriptions Data Provider Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    
    {"name":"inventoryTranslator.work.manager", "jndiName":"wm/inventory_translator", "description":"Inventory Translator Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
            
    {"name":"chweSystems.work.manager", "jndiName":"wm/chwe_systems", "description":"CHWE Systems Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
            
    {"name":"chweProbRpt.work.manager", "jndiName":"wm/chwe_problem_report", "description":"CHWE ProblemReport Work Manager", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
            
    {"name":"chweRecentEvents.work.manager", "jndiName":"wm/recent_events", "description":"CHWE Recent Events", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
            
    {"name":"chweHeartbeatEvents.work.manager", "jndiName":"wm/heartbeat_events", "description":"CHWE Heartbeat Events ", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
            
    {"name":"chweSystemSummary.work.manager", "jndiName":"wm/system_summary", "description":"CHWE System Summary", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
            
    {"name":"chweEventSummary.work.manager", "jndiName":"wm/event_summary", "description":"CHWE Event Summary", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
            
    {"name":"chweApprovePendingSystem.work.manager", "jndiName":"wm/approve_pending_system", "description":"CHWE Approve a pending system", 
        "workReqQFullAction":"0", "minThreads":"0", "numAlarmThreads":"2", "workReqQSize":"0", "maxThreads":"2",  "isGrowable":"true", 
        "threadPriority":"5",   "workTimeout":"0"},
    ]

    for wm in workmanagers:
        wmattrs = \
        '[\
          [name "%s"] \
          [jndiName "%s"] \
          [description "%s"] \
          [minThreads "%s"] \
          [maxThreads "%s"] \
          [threadPriority "%s"] \
          [isGrowable "%s"] \
          [numAlarmThreads "%s"] \
          [workReqQSize "%s"] \
          [workTimeout "%s"] \
          [workReqQFullAction "%s"] \
        ]' % (wm["name"], wm["jndiName"], wm["description"], wm["minThreads"], wm["maxThreads"], wm["threadPriority"], wm["isGrowable"], 
        wm["numAlarmThreads"], wm["workReqQSize"], wm["workTimeout"], wm["workReqQFullAction"],  )
        
        AdminConfig.create('WorkManagerInfo', server, wmattrs) 
    
    print "Created %s work managers" % len(workmanagers)
    
    print doneMarker
#enddef createWorkManagers


def testDataSources():
    print "testing data sources"

    def testDataSource(server, providerName, dataSourceName) :
        # check to see if the datasource already exists
        dataSource = AdminConfig.getid("/Server:"+server+"/JDBCProvider:"+providerName+"/DataSource:"+dataSourceName+"/")

        print 'Testing datasource %s connection...' % (dataSourceName)
        print AdminControl.testConnection(dataSource)
        return
    #enddef    

    providerName = "DB2 Universal JDBC Driver Provider (XA)"
    db2provider = AdminConfig.getid('/Server:'+myServerName+'/JDBCProvider:'+providerName+'/')

    testDataSource(myServerName, providerName, "GcsDB")  
    testDataSource(myServerName, providerName, "QuestDB")  
    testDataSource(myServerName, providerName, "SCSIDB")  
    testDataSource(myServerName, providerName, "SPEDB")  
    testDataSource(myServerName, providerName, "SPE_CST")  
    testDataSource(myServerName, providerName, "SPE_TILT")  

    print doneMarker
#enddef testDataSources


# start configuration process

createJDBCProvider()
createDataSources()
applySSLCerts()
createServletCaches()
createWorkManagers()

#Can't test data souces until after we save. If we got here, should be error free, so...

print "Everything is looking good. Saving changes so we can test the data sources..."
AdminConfig.save()

testDataSources()

print "Yay! Your server is configured" 

