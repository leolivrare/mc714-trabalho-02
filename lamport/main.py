import logging
import os
import random
import time
import uuid

from confluent_kafka import Consumer, Producer
from utils import consume_message, produce_messages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def simulate_lamport_clock(producer, consumer, process_id):
    """
    Simulates the Lamport logical clock for a given process.

    Args:
        producer: The producer object used to send messages.
        consumer: The consumer object used to receive messages.
        process_id: The ID of the current process.

    Returns:
        None
    """
    lamport_time = 0
    while True:
        start_time = time.time()
        produce_time = random.randint(1, 3)
        while time.time() - start_time < produce_time:
            lamport_time = produce_messages(
                producer, "lamport_test_1", process_id, lamport_time
            )
            time.sleep(1)

        start_time = time.time()
        consume_time = random.randint(2, 5)
        while time.time() - start_time < consume_time:
            (_, lamport_time) = consume_message(consumer, process_id, lamport_time)


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
