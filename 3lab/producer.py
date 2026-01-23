import json
from kafka import KafkaProducer
from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def validate_input(table, columns, data):
    if not table:
        raise ValueError("Имя таблицы пустое")
    if not isinstance(columns, dict):
        raise ValueError("Столбцы должны быть словарём")
    if not isinstance(data, list):
        raise ValueError("Данные должны быть списком")
    for row in data:
        if set(row.keys()) != set(columns.keys()):
            raise ValueError("Столбцы данных не совпадают со схемой")

def send_to_kafka(table, columns, data):
    validate_input(table, columns, data)

    message = {
        "table": table,
        "columns": columns,
        "data": data
    }

    producer.send(KAFKA_TOPIC, message)
    producer.flush()
    print("Данные отправлены в Kafka")

if __name__ == "__main__":
    table = "students"

    columns = {
        "id": "INTEGER",
        "name": "TEXT",
        "age": "INTEGER"
    }

    data = [
        {"id": 1, "name": "Ivan", "age": 20},
        {"id": 2, "name": "Anna", "age": 22}
    ]

    try:
        send_to_kafka(table, columns, data)
    except Exception as e:
        print("Ошибка Producer:", e)