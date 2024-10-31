"""
About
=====

Example program to demonstrate connecting to CrateDB using
its Python DB API driver, and the HTTP protocol.


Setup
=====
::

    pip install --upgrade crate


Synopsis
========
::

    # Run CrateDB
    docker run --rm -it --publish=4200:4200 crate

    # Invoke example program.
    time python insert_basic.py

"""
import sys
import datetime as dt
from pprint import pprint

import crate.client


def insert_basic():
    """
    Demonstrate a basic conversation with CrateDB, inserting a record including a timestamp.
    """
    connection = crate.client.connect("http://localhost:4200")
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS testdrive.foo;")
    cursor.execute("CREATE TABLE testdrive.foo (id INT, timestamp TIMESTAMP WITH TIME ZONE);")
    cursor.execute("INSERT INTO testdrive.foo (id, timestamp) VALUES (42, 23423434);")
    cursor.execute("INSERT INTO testdrive.foo (id, timestamp) VALUES (43, ?);", parameters=[dt.datetime.now()])
    cursor.execute("INSERT INTO testdrive.foo (id, timestamp) VALUES (44, ?);", parameters=[dt.datetime.now(tz=dt.timezone.utc)])
    cursor.execute("REFRESH TABLE testdrive.foo;")
    cursor.execute("SELECT * FROM testdrive.foo;")
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    pprint(results)


if __name__ == "__main__":
    insert_basic()
