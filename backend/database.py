import psycopg2
from psycopg2 import pool

database = {
    "host": "localhost",
    "port": "5432",
    "user": "alextrg914",
    "password": "914159",
    "database": "flight_booking"
}

def create_connection_pool():
    return psycopg2.pool.SimpleConnectionPool(1, 5, **database)

connection_pool = create_connection_pool()