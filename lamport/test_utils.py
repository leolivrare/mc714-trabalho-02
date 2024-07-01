import json
import time
import unittest
import uuid

from confluent_kafka import Consumer, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic
from utils import consume_message, produce_messages


class KafkaTestCase(unittest.TestCase):
    def setUp(self):
        conf = {"bootstrap.servers": "broker:29092"}
        self.producer = Producer(conf)
        self.consumer = Consumer(
            {
                "bootstrap.servers": "broker:29092",
                "group.id": "test",
                "auto.offset.reset": "earliest",
            }
        )

        # Create a unique topic
        self.topic = f"lamport_test_{uuid.uuid4()}"
        self.admin_client = AdminClient(conf)
        topic_config = {"num_partitions": 1, "replication_factor": 1}
        self.admin_client.create_topics([NewTopic(self.topic, **topic_config)])

        # Wait for the topic to be created
        while self.topic not in self.admin_client.list_topics().topics:
            time.sleep(1)

    def tearDown(self):
        self.consumer.close()

        # Delete the unique topic
        self.admin_client.delete_topics([self.topic])


class TestProduceMessages(KafkaTestCase):
    def test_produce_messages(self):
        process_id = "Process_1234"
        lamport_time = 0

        expected_message = {"process_id": process_id, "lamport_time": lamport_time + 1}

        produce_messages(self.producer, self.topic, process_id, lamport_time)

        # Subscribe to the topic
        self.consumer.subscribe([self.topic])

        # Consume the message
        msg = self.consumer.poll(10.0)

        if msg is None:
            self.fail("No message received")
        elif not msg.error():
            received_message = json.loads(msg.value().decode("utf-8"))
            self.assertEqual(received_message, expected_message)
        elif msg.error().code() != KafkaError._PARTITION_EOF:
            self.fail(msg.error())


class TestConsumeMessages(KafkaTestCase):
    def test_consumer_selects_producers_lamport_time(self):
        process_id_producer = "Process_1"
        process_id_consumer = "Process_2"
        consumer_lamport_time = 0
        producer_lamport_time = 10

        # Increment producer's Lamport time by 1
        produce_messages(
            self.producer, self.topic, process_id_producer, producer_lamport_time
        )

        expected_message = {"process_id": process_id_producer, "lamport_time": producer_lamport_time + 1}

        # Subscribe to the topic
        self.consumer.subscribe([self.topic])

        (msg, new_lamport_time) = consume_message(
            self.consumer, process_id_consumer, consumer_lamport_time
        )

        assert msg == expected_message

        assert new_lamport_time == producer_lamport_time + 2

    def test_consumer_selects_consumers_lamport_time(self):
        process_id_producer = "Process_1"
        process_id_consumer = "Process_2"
        consumer_lamport_time = 5
        producer_lamport_time = 0

        # Increment producer's Lamport time by 1
        produce_messages(
            self.producer, self.topic, process_id_producer, producer_lamport_time
        )

        expected_message = {"process_id": process_id_producer, "lamport_time": producer_lamport_time + 1}

        # Subscribe to the topic
        self.consumer.subscribe([self.topic])

        (msg, new_lamport_time) = consume_message(
            self.consumer, process_id_consumer, consumer_lamport_time
        )

        assert msg == expected_message

        assert new_lamport_time == consumer_lamport_time + 1


if __name__ == "__main__":
    unittest.main()
