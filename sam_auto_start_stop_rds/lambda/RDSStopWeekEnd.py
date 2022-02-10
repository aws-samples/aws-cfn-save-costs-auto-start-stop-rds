import boto3
import time
import datetime
import os

def set_region_tz():
    timezone_var = None
    #print(os.environ)

    time_now = datetime.datetime.now()
    print("Time Now : " + str(time_now))

    try:
        timezone_var = os.environ['REGION_TZ']
        print("Lambda Environment Variable Key REGION_TZ available : " + str(timezone_var))
    except Exception as e:
        timezone_var = os.environ['TZ']
        print("Lambda Environment Variable Key REGION_TZ not available : " + str(timezone_var))
    print("Timezone Var : " + str(timezone_var))

    if timezone_var is None or timezone_var == '':
        timezone = 'UTC'
    else:
        timezone = timezone_var
    print("Timezone : " + str(timezone))

    os.environ['TZ'] = str(timezone)
    time.tzset()
    return

def lambda_handler(event, context):
    flag = False
    set_region_tz()

    time_now = datetime.datetime.now()
    print("Time Now : " + str(time_now))
    week_day = datetime.datetime.now().isoweekday()  # Monday is 1 and Sunday is 7
    time_plus = time_now + datetime.timedelta(minutes=5)
    time_minus = time_now - datetime.timedelta(minutes=5)
    aest_time = format(time_now, '%H:%M')
    print("Week Day : " + str(week_day))
    print("Time Now in HH:MM : " + aest_time)
    max_aest_time = format(time_plus,'%H:%M')
    min_aest_time = format(time_minus,'%H:%M')
    count = 0

    region = os.environ['AWS_REGION']
    print("Region : " + str(region))

    rds = boto3.client('rds', region_name=region)
    dbs = rds.describe_db_instances()

    readReplica = []
    for db in dbs['DBInstances']:
        readReplicaDB = db['ReadReplicaDBInstanceIdentifiers']
        readReplica.extend(readReplicaDB)
        #print("readReplicaDB : " + str(readReplicaDB))
    print("readReplica : " + str(readReplica))

    for db in dbs['DBInstances']:
        count = count + 1
        db_id = db['DBInstanceIdentifier']
        db_id_readreplica = db['ReadReplicaDBInstanceIdentifiers']
        db_engine = db['Engine']
        print("DB ID : " + str(db_id))
        print("DB ID Read Replica : " + str(db_id_readreplica))
        print("DB Engine : " + str(db_engine))

        if db_engine not in ['aurora-mysql','aurora-postgresql']:
            if db_id not in readReplica and len(db_id_readreplica) == 0:
                instance_arn = db['DBInstanceArn']
                instance_tags = rds.list_tags_for_resource(ResourceName=instance_arn)
                db_tags = instance_tags['TagList']
                print("All Tags : " + str(db_tags))

                tag = next(iter(filter(lambda tag: tag['Key'] == 'StopWeekEnd', db_tags)), None)
                print("Tag : " + str(tag))

                if tag:
                    tag_key = tag['Key']
                    print("Tag Key : " + str(tag_key))

                    tag_value = tag['Value']
                    print("Tag Value : " + str(tag_value))

                    if tag_key and tag_value:
                        target_db = db
                        #print("DB Details : " + str(target_db))
                        db_id = target_db['DBInstanceIdentifier']
                        db_status = target_db['DBInstanceStatus']
                        print("DB ID : " + str(db_id))
                        print("DB Status : " + str(db_status))

                        if (min_aest_time <= tag_value <= max_aest_time and 6 <= week_day <= 7):
                            if db_status == "available":
                                StopWeekEnd = rds.stop_db_instance(DBInstanceIdentifier=db_id)
                                print("Stopping DB : " + str(db_id))
                            else:
                                print("Database not in Available or Running state : " + str(db_id))
                        else:
                            print("Database not available to Stop in given Week End or Time Schedule : " + str(db_id))
                    else:
                        print("Either Tag Key or Tag Value is not set for Database to Stop : " + str(tag_key))
                else:
                    print("StopWeekEnd Tag Key not set for Database to Stop")
            else:
                print("Read Replica Database not allowed to Stop : " + str(db_id))
        else:
            print("Aurora Engine Database")


    readReplica = []
    dbs = rds.describe_db_clusters()
    for db in dbs['DBClusters']:
        #readReplicaDB = db['ReadReplicaDBClusterIdentifiers']
        readReplicaDB = db['ReadReplicaIdentifiers']
        readReplica.extend(readReplicaDB)
    print("readReplica : " + str(readReplica))

    for db in dbs['DBClusters']:
        count = count + 1
        db_id = db['DBClusterIdentifier']
        #db_id_readreplica = db['ReadReplicaDBClusterIdentifiers']
        db_id_readreplica = db['ReadReplicaIdentifiers']
        db_engine = db['Engine']
        print("DB ID : " + str(db_id))
        print("DB ID Read Replica : " + str(db_id_readreplica))
        print("DB Engine : " + str(db_engine))

        if db_engine in ['aurora-mysql','aurora-postgresql']:
            if db_id not in readReplica and len(db_id_readreplica) == 0:
                instance_arn = db['DBClusterArn']
                instance_tags = rds.list_tags_for_resource(ResourceName=instance_arn)
                db_tags = instance_tags['TagList']
                print("All Tags : " + str(db_tags))

                tag = next(iter(filter(lambda tag: tag['Key'] == 'StopWeekEnd', db_tags)), None)
                print("Tag : " + str(tag))

                if tag:
                    tag_key = tag['Key']
                    print("Tag Key : " + str(tag_key))

                    tag_value = tag['Value']
                    print("Tag Value : " + str(tag_value))

                    if tag_key and tag_value:
                        target_db = db
                        #print("DB Details : " + str(target_db))
                        db_id = target_db['DBClusterIdentifier']
                        db_status = target_db['Status']
                        print("DB ID : " + str(db_id))
                        print("DB Status : " + str(db_status))

                        if (min_aest_time <= tag_value <= max_aest_time and 6 <= week_day <= 7):
                            if db_status == "available":
                                StopWeekEnd = rds.stop_db_cluster(DBClusterIdentifier=db_id)
                                print("Stopping Cluster DB : " + str(db_id))
                            else:
                                print("Cluster Database not in Available or Running state : " + str(db_id))
                        else:
                            print("Cluster Database not available to Stop in given Week End or Time Schedule : " + str(db_id))
                    else:
                        print("Either Tag Key or Tag Value is not set for Cluster Database to Stop : " + str(tag_key))
                else:
                    print("StopWeekEnd Tag Key not set for Cluster Database to Stop")
            else:
                print("Read Replica Cluster Database not allowed to Stop : " + str(db_id))

    print("Total Instance Count : " + str(count))
