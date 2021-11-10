#!/usr/bin/env python3

# preparing
# apt-get update; apt-get install pip
# pip install azure-cosmos

import cm_utils
import config
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

import datetime
import random

# pip3 install faker
from faker import Faker
fake = Faker('en_US')


ACCOUNT_HOST = config.settings['host']
ACCOUNT_KEY = config.settings['master_key']
COSMOS_DATABASE = config.settings['database_id']


def get_card_master(id, name, price, rarity, url):
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    card_master = {
        "id": "card_{}".format(id),
        "Name": "card_{}".format(name),
        "Price": price,
        "Rarity": rarity,
        "ImageURL": url + "card_{}.jpg".format(id),
        "CreateAt": dt,
        "UpdateAt": dt,
    }

    return card_master


def get_gacha_master(id, url):
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    gacha_master = {
        "id": "gacha_{}".format(id),
        "ImageURL": url + "gacha_{}.jpg".format(id),
        "CreateAt": dt,
        "UpdateAt": dt,
    }

    return gacha_master


def get_item_master(id, name, price, rarity, count, url):
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    item_master = {
        "id": "item_{}".format(id),
        "Name": "item_{}".format(name),
        "Price": price,
        "Rarity": rarity,
        "Count": count,
        "ImageURL": url + "item_{}.jpg".format(id),
        "CreateAt": dt,
        "UpdateAt": dt,
    }

    return item_master


def get_quest_master(id, url):
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    quest_master = {
        "id": "quest_{}".format(id),
        "ImageURL": url + "quest_{}.jpg".format(id),
        "CreateAt": dt,
        "UpdateAt": dt,
    }

    return quest_master


def get_user_account(id, cm_list, gm_list, im_list, qm_list):
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cards = random.choices(cm_list, k=random.randint(5, 300))
    deck = random.choices(cards, k=5)
    gachas = random.choices(gm_list, k=random.randint(0, len(gm_list)))
    items = random.choices(im_list, k=random.randint(0, len(im_list)))
    quests = random.choices(qm_list, k=random.randint(0, len(qm_list)))

    rank = random.randint(1, 100)
    exp = rank * 100 + random.randint(1, 99)
    money = random.randint(0, 10000)
    stamina = random.randint(rank * 100, rank * 150)

    user_account = {
        "id": "user_{}".format(id),
        "Name": fake.name(),
        "Rank": rank,
        "Exp": exp,
        "Money": money,
        "Stamina": stamina,
        "Cards": cards,
        "Deck": {
            "Cards": deck,
            "CreateAt": dt,
            "UpdateAt": dt,
        },
        "Items": items,
        "Quests": quests,
        "Gachas": gachas,
        "CreateAt": dt,
        "UpdateAt": dt,
    }

    return user_account


def delete_containers():
    client = cosmos_client.CosmosClient(
        ACCOUNT_HOST, {'masterKey': ACCOUNT_KEY})
    try:
        print("Delete Containers...")
        db = client.get_database_client(COSMOS_DATABASE)

        containers = list(db.list_containers())
        for cont in containers:
            try:
                db.delete_container(cont['id'])
            except exceptions.CosmosResourceNotFoundError:
                print('A container with id \'{0}\' does not exist'.format(
                    cont['id']))

    except exceptions.CosmosHttpResponseError as e:
        print('\nclear_login has caught an error. {0}'.format(e.message))

    finally:
        print("\nclear_login done")


def prepare_pilot_db():
    client = cosmos_client.CosmosClient(
        ACCOUNT_HOST, {'masterKey': ACCOUNT_KEY})
    try:
        print("Creating DB...")
        db = client.create_database_if_not_exists(id=COSMOS_DATABASE)

        print("Creating Card Master...")
        cm_container = db.create_container_if_not_exists(
            id='CardMaster', partition_key=PartitionKey(path='/id', kind='Hash'))
        for i in range(50):
            card_master = get_card_master(
                i, i, 100, 0.1, 'https://cardgame.blob.core.windows.net/cards/images/')
            cm_container.create_item(body=card_master)

        gm_container = db.create_container_if_not_exists(
            id='GachaMaster', partition_key=PartitionKey(path='/id', kind='Hash'))
        for i in range(10):
            gacha_master = get_gacha_master(
                i, 'https://cardgame.blob.core.windows.net/gachas/images/')
            gm_container.create_item(body=gacha_master)

        print("Creating Item Master...")
        im_container = db.create_container_if_not_exists(
            id='ItemMaster', partition_key=PartitionKey(path='/id', kind='Hash'))
        for i in range(100):
            item_master = get_item_master(
                i, i, 100, 0.1, 10, 'https://cardgame.blob.core.windows.net/items/images/')
            im_container.create_item(body=item_master)

        print("Creating Quest Master...")
        qm_container = db.create_container_if_not_exists(
            id='QuestMaster', partition_key=PartitionKey(path='/id', kind='Hash'))
        for i in range(10):
            quest_master = get_quest_master(
                i, 'https://cardgame.blob.core.windows.net/quests/images/')
            qm_container.create_item(body=quest_master)

        print("Reading Master data...")
        cm_list = cm_utils.read_items(cm_container, 0)
        gm_list = cm_utils.read_items(gm_container, 0)
        im_list = cm_utils.read_items(im_container, 0)
        qm_list = cm_utils.read_items(qm_container, 0)

        print("Creating User Accounts...")
        ua_container = db.create_container_if_not_exists(
            id='UserAccount', partition_key=PartitionKey(path='/id', kind='Hash'))
        offer = ua_container.read_offer()
        ua_container.replace_throughput(4000)
        for i in range(10000):
            print("# of added user account: {} of {}".format(i+1, 10000))
            user_account = get_user_account(
                i, cm_list, gm_list, im_list, qm_list)
            ua_container.create_item(body=user_account)

    except exceptions.CosmosHttpResponseError as e:
        print('\nprepare_pilot_db has caught an error. {0}'.format(e.message))

    finally:
        print("\nprepare_pilot_db done")


if __name__ == '__main__':
    delete_containers()
    prepare_pilot_db()
