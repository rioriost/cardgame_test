#!/usr/bin/env python3

# preparing
# apt-get update; apt-get install pip
# pip install azure-cosmos

import cm_utils
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions

import config

ACCOUNT_HOST = config.settings['host']
ACCOUNT_KEY = config.settings['master_key']
COSMOS_DATABASE = config.settings['database_id']


def make_match():
    client = cosmos_client.CosmosClient(
        ACCOUNT_HOST, {'masterKey': ACCOUNT_KEY})
    try:
        print("Connecting DB...")
        db = client.get_database_client(COSMOS_DATABASE)

        print("Picking a users...\n")
        lg_container = db.get_container_client(container='Login')

        for i in range(100):
            user_account = cm_utils.pick_login_user(lg_container)
            challenger = cm_utils.pick_challenger(
                lg_container, user_account['id'], user_account['Rank'])
            print("Login User: {}, Rank: {}, Login Date: {}".format(
                user_account['id'], user_account['Rank'], user_account['CreateAt']))
            print("Challenger: {}, Rank: {}, Login Date: {}\n".format(
                challenger['id'], challenger['Rank'], challenger['CreateAt']))

    except exceptions.CosmosHttpResponseError as e:
        print('\nmake_match has caught an error. {0}'.format(e.message))

    finally:
        print("\nmake_match done")


if __name__ == '__main__':
    make_match()
