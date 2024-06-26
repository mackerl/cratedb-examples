"""
About
=====

Evaluate inserting data from pandas dataframes into CrateDB.

Example program to demonstrate efficient batched inserts using CrateDB and
pandas, based on SQLAlchemy's `insertmanyvalues` vs. CrateDB's bulk import
HTTP endpoint.

- https://docs.sqlalchemy.org/core/connections.html#controlling-the-batch-size
- https://crate.io/docs/crate/reference/en/latest/interfaces/http.html#bulk-operations


Setup
=====
::

    pip install --upgrade click colorlog pandas sqlalchemy-cratedb


Synopsis
========
::

    # Run CrateDB.
    docker run --rm -it --publish=4200:4200 crate:latest

    # Use local CrateDB.
    time python insert_pandas.py

    # Use local CrateDB with "basic" mode.
    time python insert_pandas.py --mode=basic --insertmanyvalues-page-size=5000

    # Use local CrateDB with "bulk" mode, and a few more records.
    time python insert_pandas.py --mode=bulk --bulk-size=20000 --num-records=75000

    # Use CrateDB Cloud.
    time python insert_pandas.py --dburi='crate://admin:<PASSWORD>@example.aks1.westeurope.azure.cratedb.net:4200?ssl=true'


Details
=======
To watch the HTTP traffic to your local CrateDB instance, invoke::

    sudo ngrep -d lo0 -Wbyline port 4200

"""
import logging

import click
import sqlalchemy as sa
from pueblo.testing.pandas import makeTimeDataFrame
from pueblo.util.logging import setup_logging
from sqlalchemy_cratedb.support import insert_bulk

logger = logging.getLogger(__name__)


SQLALCHEMY_LOGGING = True


class DatabaseWorkload:

    table_name = "testdrive_pandas"

    def __init__(self, dburi: str):
        self.dburi = dburi

    def get_engine(self, **kwargs):
        return sa.create_engine(self.dburi, **kwargs)

    def process(self, mode: str, num_records: int, bulk_size: int, insertmanyvalues_page_size: int):
        """
        Exercise different insert methods of pandas, SQLAlchemy, and CrateDB.
        """

        logger.info(f"Creating DataFrame with {num_records} records")

        # Create a DataFrame to feed into the database.
        df = makeTimeDataFrame(nper=num_records, freq="S")
        print(df)

        logger.info(f"Connecting to {self.dburi}")
        logger.info(f"Importing data with mode={mode}, bulk_size={bulk_size}, insertmanyvalues_page_size={insertmanyvalues_page_size}")

        engine = self.get_engine(insertmanyvalues_page_size=insertmanyvalues_page_size)

        # SQLAlchemy "Insert Many Values" mode. 40K records/s
        # https://docs.sqlalchemy.org/en/20/core/connections.html#engine-insertmanyvalues
        # https://docs.sqlalchemy.org/en/20/core/connections.html#engine-insertmanyvalues-page-size
        if mode == "basic":
            # Using `chunksize` does not make much of a difference here,
            # because chunking will be done by SQLAlchemy already.
            df.to_sql(name=self.table_name, con=engine, if_exists="replace", index=False)
            # df.to_sql(name=self.table_name, con=engine, if_exists="replace", index=False, chunksize=bulk_size)

        # Multi-row mode. It is slower.
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html
        elif mode == "multi":
            df.to_sql(name=self.table_name, con=engine, if_exists="replace", index=False, chunksize=bulk_size, method="multi")

        # CrateDB bulk transfer mode. 65K records/s
        # https://crate.io/docs/crate/reference/en/latest/interfaces/http.html#bulk-operations
        elif mode == "bulk":
            df.to_sql(name=self.table_name, con=engine, if_exists="append", index=False, chunksize=bulk_size, method=insert_bulk)

        else:  # pragma: nocover
            raise ValueError(f"Unknown mode: {mode}")

    def show_table_stats(self):
        """
        Display number of records in table.
        """
        engine = self.get_engine()
        with engine.connect() as conn:
            conn.exec_driver_sql(f"REFRESH TABLE {self.table_name};")
            result = conn.exec_driver_sql(f"SELECT COUNT(*) FROM {self.table_name};")
            table_size = result.scalar_one()
            logger.info(f"Table size: {table_size}")
        #engine.dispose()


def tweak_log_levels(level=logging.INFO):

    # Enable SQLAlchemy logging.
    if SQLALCHEMY_LOGGING:
        logging.getLogger("sqlalchemy").setLevel(level)


@click.command()
@click.option("--dburi", type=str, default="crate://localhost:4200", required=False, help="SQLAlchemy database connection URI.")
@click.option("--mode", type=click.Choice(['basic', 'multi', 'bulk']), default="bulk", required=False, help="Insert mode.")
@click.option("--num-records", type=int, default=23_000, required=False, help="Number of records to insert.")
@click.option("--bulk-size", type=int, default=5_000, required=False, help="Bulk size / chunk size.")
@click.option("--insertmanyvalues-page-size", type=int, default=1_000, required=False, help="Page size for SA's insertmanyvalues.")
@click.help_option()
def main(dburi: str, mode: str, num_records: int, bulk_size: int, insertmanyvalues_page_size: int):
    setup_logging()
    tweak_log_levels()
    dbw = DatabaseWorkload(dburi=dburi)
    dbw.process(mode, num_records, bulk_size, insertmanyvalues_page_size)
    dbw.show_table_stats()


if __name__ == "__main__":
    main()
