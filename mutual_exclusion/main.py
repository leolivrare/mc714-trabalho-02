import logging
import os
import random
import time
import uuid

from confluent_kafka import Consumer, Producer
from utils import consume_message, produce_messages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sort_message_queue(message_queue):
    message_queue.sort(key=lambda x: (x['lamport_time'], x['process_id']))

def remove_from_queue(message_queue, sender_id):
    # Filter the message_queue to find all messages with the matching sender_id
    matching_messages = [message for message in message_queue if message['process_id'] == sender_id]

    # If there are no matching messages, there's nothing to remove
    if not matching_messages:
        return

    # Find the message with the smallest lamport_time among the matching messages
    message_to_remove = min(matching_messages, key=lambda x: x['lamport_time'])

    # Remove the message from the message_queue
    message_queue.remove(message_to_remove)

def request_critical_section(
    producer, consumer, process_id, lamport_time, message_queue
):
    logger.info(f"Process {process_id} is requesting critical section.")
    lamport_time = produce_messages(
        producer,
        "mutual_exclusion_test_1",
        process_id,
        lamport_time,
        content={"event": "request"},
    )

    message_queue.append({"lamport_time": lamport_time, "process_id": process_id})
    sort_message_queue(message_queue)
    logger.info(f"Process {process_id} updated message queue: {message_queue}")

    acknowledged = set()

    while True:
        message, lamport_time = consume_message(consumer, process_id, lamport_time)

        if message is not None:
            if message["process_id"] == process_id:
                continue

            event = message["event"]
            sender_id = message["process_id"]
            sender_time = message["lamport_time"]

            if event == "reply":
                acknowledged.add(sender_id)

            elif event == "request":
                message_queue.append({"lamport_time": sender_time, "process_id": sender_id})
                sort_message_queue(message_queue)
                logger.info(f"Process {process_id} updated message queue: {message_queue}")

                lamport_time = produce_messages(
                    producer,
                    "mutual_exclusion_test_1",
                    process_id,
                    lamport_time,
                    content={"event": "reply"},
                )

            elif event == "release":
                try:
                    remove_from_queue(message_queue, sender_id)
                    sort_message_queue(message_queue)
                    logger.info(f"Process {process_id} updated message queue: {message_queue}")
                except ValueError:
                    pass
        logger.info(f"Process {process_id} updated acknowledged: {acknowledged}")
        if (
            message_queue[0]['process_id'] == process_id and len(acknowledged) == 2
        ):  # Assuming there are 3 processes in total
            break

    logger.info(f"Process {process_id} is entering critical section.")
    time.sleep(random.randint(1, 5))

    message_queue.pop(0)
    logger.info(f"Process {process_id} updated message queue: {message_queue}")

    lamport_time = produce_messages(
        producer,
        "mutual_exclusion_test_1",
        process_id,
        lamport_time,
        content={"event": "release"},
    )

    logger.info(f"Process {process_id} has left critical section.")
    return lamport_time, message_queue


def listen_and_reply(producer, consumer, process_id, lamport_time, message_queue):
    logger.info(
        f"Process {process_id} is executing other actions outside of the critical section."
    )
    start_time = time.time()
    duration = random.randint(3, 5)

    while True:
        if time.time() - start_time > duration:
            break

        message, lamport_time = consume_message(consumer, process_id, lamport_time)

        if message is not None:
            if message["process_id"] == process_id:
                continue
            event = message["event"]
            sender_id = message["process_id"]
            sender_time = message["lamport_time"]

            if event == "request":
                message_queue.append({"lamport_time": sender_time, "process_id": sender_id})
                sort_message_queue(message_queue)
                logger.info(f"Process {process_id} updated message queue: {message_queue}")

                lamport_time = produce_messages(
                    producer,
                    "mutual_exclusion_test_1",
                    process_id,
                    lamport_time,
                    content={"event": "reply"},
                )

            elif event == "release":
                try:
                    remove_from_queue(message_queue, sender_id)
                    sort_message_queue(message_queue)
                    logger.info(f"Process {process_id} updated message queue: {message_queue}")
                except ValueError:
                    pass
        else:
            lamport_time += 1
            logger.info(
                f"Process {process_id} is executing other actions outside of the critical section. Lamport time: {lamport_time}"
            )

    return lamport_time, message_queue


def simulate_mutual_exclusion(producer, consumer, process_id):
    lamport_time = 0
    message_queue = []

    while True:
        if random.choice([True, False]):
            lamport_time, message_queue = request_critical_section(
                producer, consumer, process_id, lamport_time, message_queue
            )
        else:
            lamport_time, message_queue = listen_and_reply(
                producer, consumer, process_id, lamport_time, message_queue
            )


if __name__ == "__main__":
    producer = Producer({"bootstrap.servers": "broker:29092"})
    consumer = Consumer(
        {
            "bootstrap.servers": "broker:29092",
            "group.id": os.getenv("PROCESS_ID", f"Process_{str(uuid.uuid4())[:4]}"),
            "auto.offset.reset": "earliest",
        }
    )
    consumer.subscribe(["mutual_exclusion_test_1"])

    process_id = os.getenv("PROCESS_ID", f"Process_{str(uuid.uuid4())[:4]}")

    logger = logging.getLogger(process_id)
    logger.info(f"Starting process with ID: {process_id}")

    simulate_mutual_exclusion(producer, consumer, process_id)

    consumer.close()