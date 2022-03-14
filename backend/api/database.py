from contextlib import contextmanager

import psycopg2

from . import logger

_logger = logger.setup(__name__)


@contextmanager
def connect(url, **connection_kwargs):
    try:
        connection = psycopg2.connect(url, **connection_kwargs)
        cursor = connection.cursor()
        yield connection, cursor
    finally:
        connection.commit()
        cursor.close()
        connection.close()


def get_random_birds(state, n_birds, n_images, url):
    query = """
        WITH
            randomized_state_birds AS (
                SELECT programmatic_name
                FROM stats
                WHERE region_code = %s
                ORDER BY RANDOM()
                LIMIT %s
            ),
            randomized_images AS (
                SELECT
                    images.programmatic_name,
                    images.filepath,
                    ROW_NUMBER() OVER (PARTITION BY images.programmatic_name ORDER BY RANDOM()) AS random_index
                FROM randomized_state_birds

                LEFT JOIN images
                    ON images.programmatic_name = randomized_state_birds.programmatic_name

                WHERE images.programmatic_name IS NOT NULL AND NOT delete
            )


        SELECT programmatic_name, filepath
        FROM randomized_images
        WHERE random_index <= %s
        ;
    """
    with connect(url, curcursor_factorysor=psycopg2.extras.RealDictCursor) as (_, cursor):
        cursor.execute(query, (state, n_birds, n_images))
        return cursor.fetchall()


def get_most_common_birds(state, n_birds, n_images, url):
    query = """
        WITH
            state_birds AS (
                SELECT programmatic_name
                FROM stats
                WHERE region_code = %s
                ORDER BY abundance_mean DESC
                LIMIT %s
            ),
            randomized_images AS (
                SELECT
                    images.programmatic_name,
                    images.filepath,
                    ROW_NUMBER() OVER (PARTITION BY images.programmatic_name ORDER BY RANDOM()) AS random_index
                FROM state_birds

                LEFT JOIN images
                    ON images.programmatic_name = state_birds.programmatic_name

                WHERE NOT delete
            )

        SELECT programmatic_name, filepath
        FROM randomized_images
        WHERE random_index <= %s
        ;
    """
    with connect(url, curcursor_factorysor=psycopg2.extras.RealDictCursor) as (_, cursor):
        cursor.execute(query, (state, n_birds, n_images))
        return cursor.fetchall()


def get_specific_birds(birds, n_images, url):
    query = """
        WITH
            randomized_images AS (
                SELECT
                    programmatic_name,
                    filepath,
                    ROW_NUMBER() OVER (PARTITION BY programmatic_name ORDER BY RANDOM()) AS random_index
                FROM images

                WHERE programmatic_name IN %s AND NOT delete
            )

        SELECT programmatic_name, filepath
        FROM randomized_images
        WHERE random_index <= %s
        ;
    """
    birds = tuple(birds) if isinstance(birds, (tuple, list)) else (birds,)
    with connect(url, curcursor_factorysor=psycopg2.extras.RealDictCursor) as (_, cursor):
        cursor.execute(query, (birds, n_images))
        return cursor.fetchall()


def get_genus(genus, n_images, url):
    query = """
        WITH
            genus_birds AS (
                SELECT programmatic_name
                FROM stats
                WHERE LOWER(genus) = %s
            ),
            randomized_images AS (
                SELECT
                    images.programmatic_name,
                    images.filepath,
                    ROW_NUMBER() OVER (PARTITION BY images.programmatic_name ORDER BY RANDOM()) AS random_index
                FROM genus_birds

                LEFT JOIN images
                    ON images.programmatic_name = genus_birds.programmatic_name

                WHERE NOT delete
            )

        SELECT programmatic_name, filepath
        FROM randomized_images
        WHERE random_index <= %s
        ;
    """
    with connect(url, curcursor_factorysor=psycopg2.extras.RealDictCursor) as (_, cursor):
        cursor.execute(query, (genus.lower(), n_images))
        return cursor.fetchall()


def mark_image_for_deletion(filepath, url):
    query = """
        UPDATE images
        SET delete = True
        WHERE filepath = %s
        RETURNING programmatic_name
        ;
    """
    with connect(url, curcursor_factorysor=psycopg2.extras.RealDictCursor) as (_, cursor):
        cursor.execute(query, (filepath,))
        if cursor.rowcount > 0:
            _logger.info(
                "Found! Marking %s for deletion... Returning new image...", filepath
            )
            bird = cursor.fetchone()["programmatic_name"]
            return get_specific_birds(birds=[bird], n_images=1, url=url)
        _logger.info("%s not found...", filepath)
        return []
