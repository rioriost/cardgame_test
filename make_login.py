#!/usr/bin/env python3

# preparing
# apt-get update; apt-get install pip
# pip install azure-cosmos

import cm_utils
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

import datetime
import random
import config

ACCOUNT_HOST = config.settings['host']
ACCOUNT_KEY = config.settings['master_key']
COSMOS_DATABASE = config.settings['database_id']


def clear_login():
    client = cosmos_client.CosmosClient(
        ACCOUNT_HOST, {'masterKey': ACCOUNT_KEY})
    try:
        db = client.get_database_client(COSMOS_DATABASE)
        try:
            db.delete_container('Login')
        except exceptions.CosmosResourceNotFoundError:
            print('A container with id \'{0}\' does not exist'.format(
                'Login'))
        lg_container = db.create_container_if_not_exists(
            id='Login', partition_key=PartitionKey(path='/Rank', kind='Hash'))
    except exceptions.CosmosHttpResponseError as e:
        print('\nclear_login has caught an error. {0}'.format(e.message))

    finally:
        print("\nclear_login done")


def make_login():
    client = cosmos_client.CosmosClient(
        ACCOUNT_HOST, {'masterKey': ACCOUNT_KEY})
    try:
        print("Connecting DB...")
        db = client.get_database_client(COSMOS_DATABASE)

        print("Making logins...")
        ua_container = db.get_container_client(container='UserAccount')
        lg_container = db.get_container_client(container='Login')
        ln = cm_utils.get_len_of_cnt(ua_container)
        ids = random.sample(range(0, ln), k=int(ln*0.1))
        for id in ids:
            td = datetime.timedelta(minutes=random.randint(
                0, 60), seconds=random.randint(0, 60))
            dt = (datetime.datetime.now() - td).strftime('%Y-%m-%d %H:%M:%S')
            user_account = cm_utils.pick_user_account(
                ua_container, 'user_{}'.format(id))
            login = {
                "id": user_account['id'],
                "CreateAt": dt,
                "UserId": user_account['id'],
                "Rank": user_account['Rank']
            }
            lg_container.create_item(body=login)

    except exceptions.CosmosHttpResponseError as e:
        print('\nmake_login has caught an error. {0}'.format(e.message))

    finally:
        print("\nmake_login done")


if __name__ == '__main__':
    clear_login()
    make_login()
