from sqlalchemy import create_engine, text, select
import os


"""
Database Connection and Data Fetching Functions

This module provides functions for creating a database connection using SQLAlchemy and fetching data from a PostgreSQL database.
"""


def get_engine():
    """
    Creates a database connection using SQLAlchemy.

    Retrieves the database connection settings from environment variables and creates an engine object.

    Returns:
        engine (sqlalchemy.engine.Engine): The created engine object.
    """
    POSTGRES_HOSTNAME = os.getenv('POSTGRES_HOSTNAME')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT')
    POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE')
    POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

    engine = create_engine(
        f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOSTNAME}:{POSTGRES_PORT}/{POSTGRES_DATABASE}")

    return engine


def fetch_data(table_name, key, Session, session=None):
    """
    Fetches a value from a table in the database.

    Parameters:
    - table_name (str): The name of the table to fetch from.
    - key (str): The key to search for.
    - Session (sqlalchemy.orm.Session): The database session object.
    - session (sqlalchemy.orm.Session, optional): An alternative session object. Defaults to None.

    Returns:
    - value (any): The fetched value, or None if not found.
    """
    stmt = f"SELECT orig_key, orig_value FROM {table_name} WHERE orig_key='{key}';"

    if session is None:
        # Create a new session and begin a transaction
        session1 = Session()
        session1.begin()
        # Execute the query and retrieve the results
        res = session1.execute(text(stmt)).all()
        # Commit the transaction
        session1.commit()
        # Close the session
        session1.close()
    else:
        # Execute the query using the provided session
        res = session.execute(text(stmt)).all()

    # Check if a result was found
    if len(res) < 1:
        return None

    # Return the fetched value
    return res[0][1]


def fetch_data_auto(SourceTable, key, Session, session=None):
    """
    Fetches a value from a table in the database using the SQLAlchemy `select` method.

    Parameters:
    - SourceTable (sqlalchemy.Table): The table to fetch from.
    - key (str): The key to search for.
    - Session (sqlalchemy.orm.Session): The database session object.
    - session (sqlalchemy.orm.Session, optional): An alternative session object. Defaults to None.

    Returns:
    - value (any): The fetched value, or None if not found.
    """
    stmt = select(SourceTable).where(SourceTable.orig_key == key)

    if session is None:
        # Create a new session and begin a transaction
        session1 = Session()
        session1.begin()
        # Execute the query and retrieve the results
        res = session1.scalars(stmt).all()
        # Commit the transaction
        session1.commit()
        # Close the session
        session1.close()
    else:
        # Execute the query using the provided session
        res = session.scalars(stmt).all()

    # Check if a result was found
    if len(res) < 1:
        return None

    # Return the fetched value
    return res[0].orig_value
