#!/usr/bin/env python3

import random

def get_len_of_cnt(container):
    ln = list(container.query_items(
        query="SELECT VALUE count(1) FROM r",
        enable_cross_partition_query=True
    ))

    return ln[0]


def read_items(container, limit=0):
    item_list = []
    if limit == 0:
        items = container.read_all_items()
    else:
        items = container.read_all_items(max_item_count=limit)
    for item in items:
        item.pop("_rid")
        item.pop("_self")
        item.pop("_etag")
        item.pop("_attachments")
        item.pop("_ts")
        item_list.append(item)

    return item_list


def pick_user_account(ua_container, id):
    user_account = list(ua_container.query_items(
        query="SELECT * FROM r WHERE r.id='{}'".format(id),
        enable_cross_partition_query=True
    ))

    return user_account[0]


def pick_login_user(container):
    ln = get_len_of_cnt(container)
    user_accounts = list(container.query_items(
        query="SELECT * FROM r OFFSET {} LIMIT 1".format(
            random.randint(0, ln - 1)),
        enable_cross_partition_query=True
    ))

    return user_accounts[0]


def pick_challenger(container, except_id, rank):
    challengers = list(container.query_items(
        query="SELECT * FROM r WHERE r.Rank >= {} AND r.Rank <= {} AND r.id != '{}' ORDER BY r.CreateAt DESC OFFSET 0 LIMIT 10".format(
            rank - 5, rank + 5, except_id),
        enable_cross_partition_query=True
    ))

    return random.sample(challengers, k=1)[0]
