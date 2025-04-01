import os

from sqlalchemy import create_engine, text, select

def get_engine():
    POSTGRES_HOSTNAME = os.getenv('POSTGRES_HOSTNAME')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT')
    POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE')
    POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

    engine = create_engine(
        f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOSTNAME}:{POSTGRES_PORT}/{POSTGRES_DATABASE}")

    return engine

def fetch_data(table_name, key, Session, session=None):
    stmt = f"SELECT orig_key, orig_value FROM {table_name} WHERE orig_key='{key}';"
    
    if session is None:
        session1 = Session()
        session1.begin()
        res = session1.execute(text(stmt)).all()
        session1.commit()
        session1.close()
    else:
        res = session.execute(text(stmt)).all()
    if len(res) < 1:
        return None
    
    return res[0][1]

def fetch_data_auto(SourceTable, key, Session, session=None):
    stmt = select(SourceTable).where(SourceTable.orig_key == key)
    if session is None:
        session1 = Session()
        session1.begin()
        res = session.scalars(stmt).all()
        session1.commit()
        session1.close()
    else:
        res = session.scalars(stmt).all()
    if len(res) < 1:
        return None
    return res[0].orig_value
