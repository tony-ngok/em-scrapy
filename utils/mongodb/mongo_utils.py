import json
import os
import time
from datetime import datetime, timedelta

from pymongo import UpdateOne
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ExecutionTimeout, NetworkTimeout


def gen_uo(dat: dict, has_vars: bool = False, has_recensions: bool = False, has_ship_fee: bool = False, has_ship_date: bool = False):
    """
    插入/更新单个商品的upsert操作
    """

    updates = {
        "date": dat["date"],
        "existence": dat["existence"],
        "price": dat["price"],
        "available_qty": dat["available_qty"]
    }
    dat.pop('date')
    dat.pop('existence')
    dat.pop('price')
    dat.pop('available_qty')

    if has_vars:
        updates["variants"] = dat["variants"]
        dat.pop('variants')
    if has_recensions:
        updates["reviews"] = dat["reviews"]
        updates["rating"] = dat["rating"]
        dat.pop('reviews')
        dat.pop('rating')
    if has_ship_fee:
        updates["shipping_fee"] = dat["shipping_fee"]
        dat.pop('shipping_fee')
    if has_ship_date:
        updates["shipping_days_min"] = dat["shipping_days_min"]
        updates["shipping_days_max"] = dat["shipping_days_max"]
        dat.pop('shipping_days_min')
        dat.pop('shipping_days_max')

    query = { "_id": dat["product_id"] }
    return UpdateOne(query, {"$set": updates, "$setOnInsert": dat }, upsert=True)


def get_uos(dateiname, has_vars: bool = False, has_recensions: bool = False, has_ship_fee: bool = False, has_ship_date: bool = False):
    """
    积累所有upsert操作，以便批量处理
    """

    if isinstance(dateiname, str):
        if os.path.exists(dateiname):
            with open(dateiname, 'r', encoding='utf-8') as f:
                ops = [gen_uo(json.loads(line.strip()), has_vars, has_recensions, has_ship_fee, has_ship_date)
                    for line in f if line.strip()]
            return ops
        return []
    elif isinstance(dateiname, list):
        if dateiname:
            return [gen_uo(dat, has_vars, has_recensions, has_ship_fee, has_ship_date) for dat in dateiname]
        return []


def bulk_write(ops: list[UpdateOne], coll: Collection, max_tries: int) -> bool:
    """
    批量插入/更新商品资料
    """

    if not ops:
        return True

    for i in range(1, max_tries+1):
        try:
            bw = coll.bulk_write(ops)
            # print(bw)
            return True
        except (ConnectionFailure, ExecutionTimeout, NetworkTimeout) as op_f:
            print(f"({i}/{max_tries})", "Update error", str(op_f))
            time.sleep(2)
    return False


def update_sold_out(coll: Collection, max_tries: int, d: int = 7) -> bool:
    """
    太久没更新的商品不删掉，标注为断货
    """

    now = datetime.now()
    date_before = (now-timedelta(days=d)).strftime('%Y-%m-%dT%H:%M:%S')

    for i in range(1, max_tries+1):
        try:
            erg = coll.update_many(
                { "date": { "$lt": date_before } },
                { "$set": {
                    "date": now.strftime('%Y-%m-%dT%H:%M:%S'),
                    "existence": False,
                    "available_qty": 0
                }
                }
            )
            # print(erg)
            return True
        except Exception as e:
            print(f"({i}/{max_tries})", "Update error", str(e))
            time.sleep(2)
    return False


def exists_ids(coll: Collection, items_ids: list):
    """
    返回该批次中已存在数据中的ID
    """

    if items_ids:
        exists = coll.find({ "_id": { "$in": items_ids } }, { "_id": 1 })
        return {item["_id"] for item in exists}
    return set()
