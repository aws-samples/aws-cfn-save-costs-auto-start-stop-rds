import boto3
import os

target_db = None
region = os.environ['AWS_REGION']
rds = boto3.client('rds', region_name=region)

def get_tags_for_db(db):
    instance_arn = db['DBInstanceArn']
    instance_tags = rds.list_tags_for_resource(ResourceName=instance_arn)
    return instance_tags['TagList']

def get_tags_for_db_cluster(db):
    instance_arn = db['DBClusterArn']
    instance_tags = rds.list_tags_for_resource(ResourceName=instance_arn)
    return instance_tags['TagList']

def lambda_handler(event, context):

    dbs = rds.describe_db_instances()
    readReplica = []
    for db in dbs['DBInstances']:
        readReplicaDB = db['ReadReplicaDBInstanceIdentifiers']
        readReplica.extend(readReplicaDB)
    print("readReplica : " + str(readReplica))

    for db in dbs['DBInstances']:
        db_id = db['DBInstanceIdentifier']
        db_engine = db['Engine']
        print('DB ID : ' + str(db_id))
        db_tags = get_tags_for_db(db)
        print("All Tags : " + str(db_tags))
        tag = next(iter(filter(lambda tag: tag['Key'] == 'AutoStop' and tag['Value'].lower() == 'true', db_tags)), None)
        print("AutoStop Tag : " + str(tag))

        if db_engine not in ['aurora-mysql','aurora-postgresql']:
            if db_id not in readReplica and len(readReplica) == 0:
                if tag:
                    target_db = db
                    print("DB Details : " + str(target_db))
                    db_id = target_db['DBInstanceIdentifier']
                    db_status = target_db['DBInstanceStatus']
                    print("DB ID : " + str(db_id))
                    print("DB Status : " + str(db_status))
                    if db_status == "available":
                        AutoStopping = rds.stop_db_instance(DBInstanceIdentifier=db_id)
                        print("Stopping DB : " + str(db_id))
                    else:
                        print("Database already stopped : " + str(db_id))
                else:
                    print("AutoStop Tag Key not set for Database to Stop...")
            else:
                print("Cannot stop or start a Read-Replica Database...")

    dbs = rds.describe_db_clusters()
    readReplica = []
    for db in dbs['DBClusters']:
        readReplicaDB = db['ReadReplicaIdentifiers']
        readReplica.extend(readReplicaDB)
    print("readReplica : " + str(readReplica))

    for db in dbs['DBClusters']:
        db_id = db['DBClusterIdentifier']
        db_engine = db['Engine']
        print('DB ID : ' + str(db_id))
        db_tags = get_tags_for_db_cluster(db)
        print("All Tags : " + str(db_tags))
        tag = next(iter(filter(lambda tag: tag['Key'] == 'AutoStop' and tag['Value'].lower() == 'true', db_tags)), None)
        print("AutoStop Tag : " + str(tag))

        if db_engine in ['aurora-mysql','aurora-postgresql']:
            if db_id not in readReplica and len(readReplica) == 0:
                if tag:
                    target_db = db
                    db_id = target_db['DBClusterIdentifier']
                    db_status = target_db['Status']
                    print("Cluster DB ID : " + str(db_id))
                    print("Cluster DB Status : " + str(db_status))
                    if db_status == "available":
                        AutoStopping = rds.stop_db_cluster(DBClusterIdentifier=db_id)
                        print("Stopping Cluster DB : " + str(db_id))
                    else:
                        print("Cluster Database already stopped : " + str(db_id))
                else:
                    print("AutoStop Tag Key not set for Cluster Database to Stop...")
            else:
                print("Cannot stop or start a Read-Replica Cluster Database...")
