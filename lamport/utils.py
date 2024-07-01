import json
import logging
from typing import Any, Dict, Optional, Tuple

from confluent_kafka import Consumer, KafkaError, Message, Producer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def delivery_report(err: Optional[KafkaError], msg: Message) -> None:
    """
    Callback function to handle delivery reports for Kafka messages.

    Args:
        err (Optional[KafkaError]): The error, if any, that occurred during message delivery.
        msg (Message): The Kafka message that was delivered.

    Returns:
        None
    """
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


def produce_messages(
    producer: Producer,
    topic: str,
    process_id: int,
    lamport_time: int,
    content: Dict[str, Any] = {},
) -> int:
    """
    Produces a message to a Kafka topic using the provided producer.

    Args:
        producer (Producer): The Kafka producer instance.
        topic (str): The name of the Kafka topic to produce the message to.
        process_id (int): The ID of the process producing the message.
        lamport_time (int): The current Lamport time.
        content (Dict[str, Any], optional): Additional content to include in the message. Defaults to {}.

    Returns:
        int: The updated Lamport time after producing the message.
    """
    lamport_time += 1
    message = {"process_id": process_id, "lamport_time": lamport_time}
    message.update(content)
    producer.poll(0)
    producer.produce(
        topic, json.dumps(message).encode("utf-8"), callback=delivery_report
    )
    producer.flush()
    return lamport_time


def consume_message(
    consumer: Consumer, process_id: int, lamport_time: int
) -> Tuple[Dict[str, Any], int]:
    """
    Consume a message from the Kafka consumer and update the Lamport time.

    Args:
        consumer (Consumer): The Kafka consumer instance.
        process_id (int): The ID of the current process.
        lamport_time (int): The current Lamport time.

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing the consumed message and the updated Lamport time.
    """
    msg = consumer.poll(1.0)
    message = None
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

    elif msg is not None:
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                logger.error(msg.error())

    return (message, lamport_time)
