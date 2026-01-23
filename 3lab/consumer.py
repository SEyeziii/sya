import json
import psycopg2
from kafka import KafkaConsumer
from config import (
    KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC,
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
)

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest"
)

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cursor = conn.cursor()

def create_table(table, columns):
    cols = ", ".join([f"{k} {v}" for k, v in columns.items()])
    sql = f"CREATE TABLE IF NOT EXISTS {table} ({cols});"
    cursor.execute(sql)
    conn.commit()

def insert_data(table, data):
    for row in data:
        cols = ", ".join(row.keys())
        placeholders = ", ".join(["%s"] * len(row))
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        cursor.execute(sql, list(row.values()))
    conn.commit()

print("Consumer запущен")

for message in consumer:
    try:
        msg = message.value
        table = msg["table"]
        columns = msg["columns"]
        data = msg["data"]

        create_table(table, columns)
        insert_data(table, data)

        print(f"Таблица `{table}` успешно обработана")

    except Exception as e:
        print("Ошибка Consumer:", e)