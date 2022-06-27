import logging

import orjson
from pymongo import UpdateOne

from db.BaseModel import AsyncBaseCache, BaseDB
from etc.config import Config


async def update_users_sugg_count(db: BaseDB):
    db.reset_post_count()
    logging.info('Posts count updated')


async def upload_cache_db(db: BaseDB, cache: AsyncBaseCache):
    bulk = []
    async for post_id in cache.redis.scan_iter(f'{Config.bot_name}:post_id:*'):
        _, _, id_ = post_id.split(':')
        logging.info(id_)
        reactions = await cache.get(key=f'{Config.bot_name}:post_id:{id_}')
        logging.info(reactions)
        bulk.append(UpdateOne({'_id': int(id_)}, {'$set': orjson.loads(reactions)}), )
        await cache.delete(key=post_id)
        if len(bulk) == 500:
            result = db.bulk_push_reactions(reactions=bulk)
            logging.info(f'cache uploaded {result.bulk_api_result}')
            bulk.clear()
    if len(bulk) > 0:
        result = db.bulk_push_reactions(reactions=bulk)
        logging.info(f'cache uploaded {result.bulk_api_result}')
        bulk.clear()
