import sys
sys.path.append("..")
from utils.db.Db import Db

db = Db("../cache")

sql = """
    select 
        portfolio_data 
    from 
        monthly_portfolio_stats
    where 
        portfolio_key like '%_efficient'    
"""
cur = db.conn.cursor()
cur.execute(sql)

for result in cur.fetchall():
    print(result)