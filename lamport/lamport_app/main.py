import os
import time
import random
import uuid
import json
import logging
from confluent_kafka import Producer, Consumer, KafkaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        message = json.loads(msg.value().decode("utf-8"))
        lamport_time = message["lamport_time"]
        log_message = {
            "event": f"Delivered message with Lamport time {lamport_time} to topic {msg.topic()}",
            "lamport_time": lamport_time,
        }
        logger.info(json.dumps(log_message))


def produce_messages(producer, topic, process_id, lamport_time):
    lamport_time += 1
    message = json.dumps({"process_id": process_id, "lamport_time": lamport_time})
    producer.poll(0)
    producer.produce(
        topic, message.encode("utf-8"), callback=delivery_report
    )
    producer.flush()
    return lamport_time


def consume_message(consumer, process_id, lamport_time):
    msg = consumer.poll(1.0)

    if msg is not None and not msg.error():
        try:
            message = json.loads(msg.value().decode("utf-8"))
            received_process_id = message["process_id"]
            received_lamport_time = int(message["lamport_time"])

            if received_process_id != process_id:
                last_lamport_time = lamport_time
                lamport_time = max(last_lamport_time, received_lamport_time) + 1

                log_message = {
                    "event": f"Received message from process {received_process_id} with Lamport time {received_lamport_time}. Updated Lamport time: max({last_lamport_time}, {received_lamport_time})+1 = {lamport_time}",
                    "lamport_time": lamport_time,
                }
                logger.info(json.dumps(log_message))
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON message")

    elif msg.error():
        if msg.error().code() != KafkaError._PARTITION_EOF:
            logger.error(msg.error())

    return lamport_time


def simulate_lamport_clock(producer, consumer, process_id):
    lamport_time = 0
    while True:
        start_time = time.time()
        produce_time = random.randint(1, 3)
        while time.time() - start_time < produce_time:
            lamport_time = produce_messages(producer, "lamport_test_1", process_id, lamport_time)
            time.sleep(1)

        start_time = time.time()
        consume_time = random.randint(2, 5)
        while time.time() - start_time < consume_time:
            lamport_time = consume_message(consumer, process_id, lamport_time)


if __name__ == "__main__":
    producer = Producer({"bootstrap.servers": "broker:29092"})
    consumer = Consumer(
        {
            "bootstrap.servers": "broker:29092",
            "group.id": os.getenv("PROCESS_ID", f"Process_{str(uuid.uuid4())[:4]}"),
            "auto.offset.reset": "earliest",
        }
    )
    consumer.subscribe(["lamport_test_1"])

    process_id = os.getenv("PROCESS_ID", f"Process_{str(uuid.uuid4())[:4]}")

    logger = logging.getLogger(process_id)
    logger.info(f"Starting process with ID: {process_id}")

    simulate_lamport_clock(producer, consumer, process_id)

    consumer.close()
