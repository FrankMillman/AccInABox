import sys
import os
import importlib
import asyncio
from configparser import ConfigParser

if len(sys.argv) == 2:
    cfg_name = sys.argv[1]
else:
    cfg_name = 'aib.ini'

cfg = ConfigParser()
cfg.read(os.path.join(os.path.dirname(__file__), '..', '..', cfg_name))

sys.path.append('../..')
import db.api

db.api.config_connection(cfg['DbParams'])
db.api.config_cursor(cfg['DbParams'])

db_session = db.api.start_db_session()

async def main(incz, exp):
    if incz == 'y' and exp == 'y':
        from incz_y_exp_y import sql, params
    elif incz == 'y' and exp == 'n':
        from incz_y_exp_n import sql, params
    elif incz == 'n' and exp == 'y':
        from incz_n_exp_y import sql, params
    elif incz == 'n' and exp == 'n':
        from incz_n_exp_n import sql, params

    async with db_session.get_connection() as db_mem_conn:
        conn = db_mem_conn.db
        cur = await conn.exec_sql(sql, params)
        async for row in cur:
            print(row)

    input()


# company = input('Company: ')
# if company == '':
#     sys.exit()

incz = input('Include zeros? ')
exp = input('Expand subledgers? ')

loop = asyncio.get_event_loop()
loop.run_until_complete(db.cache.setup_companies())
loop.run_until_complete(main(incz, exp))
db.api.close_all_connections()
