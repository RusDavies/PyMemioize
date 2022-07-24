from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Sequence
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ResultIndexItem( Base ):
    __tablename__ = 'results_index'

    id          = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    metric      = Column(String)
    start       = Column(DateTime)
    end         = Column(DateTime)
    step        = Column(Integer)    
    filename    = Column(String)
    timestamp   = Column(DateTime)

    def __repr__(self):
        msg = "<ResultIndexIetm(id={}, metric='{}', start='{}', end='{}', step={}, filename='{}', timestamp='{}')>"
        msg = msg.format(self.id, self.metric, self.start, self.end, self.step, self.filename, self.timestamp)
        return msg


class CacheBackendDiskIndexer:
    def __init__(self, cache_path=None, cache_ttl=3600):
        # Set up the SQL index db
        sql_file = cache_path / 'index.sqlite3'
        engine = create_engine('sqlite:///' + str(sql_file.absolute()) )
        Base.metadata.create_all(engine)

        self.Session = sessionmaker(bind=engine)

    def PurgeAgedEntries(self):
        pass

    def DeleteItem(self):
        pass

    def AddItem(self, metric, start, end, step, filename ):
        item = ResultIndexItem(metric=metric, start=start, end=end, step=step, filename=filename, timestamp=datetime.now() )
        with self.Session() as session: 
            session.add(item)
            session.commit()
        return

    def GetItem(self, metric, start, end, step, exact=True):
        results = None
        with self.Session() as session: 
            if (exact):
                results = session.query(ResultIndexItem)\
                                .filter(metric                == metric)\
                                .filter(ResultIndexItem.start == start)\
                                .filter(ResultIndexItem.end   == end)\
                                .filter(ResultIndexItem.step  == step)
            else:
                results = session.query(ResultIndexItem)\
                                .filter(metric                == metric)\
                                .filter(ResultIndexItem.start <= start)\
                                .filter(ResultIndexItem.end   >= end)\
                                .filter(ResultIndexItem.step  >= step)
        
        return results



if (__name__ == '__main__'):
    
    cache_path = Path('./.cache_tmp/')
    sql_file = (cache_path / 'index.sqlite3')
    if ( sql_file.exists()):
        sql_file.unlink()

    cacheIndexer = CacheBackendDiskIndexer(cache_path=cache_path)

    end = datetime.now()
    start = end - timedelta(hours=1)

    # Add an item
    cacheIndexer.AddItem('test', start=start, end=end, step=100, filename='abcdefg')

    # Retrieve the item as exact
    results = cacheIndexer.GetItem('test', start=start, end=end, step=100)

    for item in results:
        print(item)

