import unittest
import uuid
import time
from main import remove_from_queue, sort_message_queue, request_critical_section
from confluent_kafka import Consumer, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic
from utils import consume_message, produce_messages

class TestRemoveFromQueue(unittest.TestCase):
    def test_remove_from_queue(self):
        message_queue = [
            {"lamport_time": 1, "process_id": 2},
            {"lamport_time": 2, "process_id": 4},
            {"lamport_time": 3, "process_id": 5},
            {"lamport_time": 4, "process_id": 2},
        ]
        sender_id = 2

        remove_from_queue(message_queue, sender_id)

        expected_queue = [
            {"lamport_time": 2, "process_id": 4},
            {"lamport_time": 3, "process_id": 5},
            {"lamport_time": 4, "process_id": 2},
        ]

        self.assertEqual(message_queue, expected_queue)

class TestSortMessageQueue(unittest.TestCase):
    def test_sort_message_queue(self):
        message_queue = [
            {"lamport_time": 3, "process_id": 5},
            {"lamport_time": 1, "process_id": 2},
            {"lamport_time": 4, "process_id": 2},
            {"lamport_time": 2, "process_id": 4},
        ]

        sort_message_queue(message_queue)

        expected_queue = [
            {"lamport_time": 1, "process_id": 2},
            {"lamport_time": 2, "process_id": 4},
            {"lamport_time": 3, "process_id": 5},
            {"lamport_time": 4, "process_id": 2},
        ]

        self.assertEqual(message_queue, expected_queue)


class KafkaTestCase(unittest.TestCase):
    """
    A test case class for testing Kafka functionality.

    This class provides setup and teardown methods for creating and deleting a unique Kafka topic,
    as well as initializing a Kafka producer and consumer for testing purposes.
    """

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
        self.topic = f"mutual_exclusion_{uuid.uuid4()}"
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

class TestRequestCriticalSection(KafkaTestCase):
    def test_request_critical_section(self):
        process_id = 1
        lamport_time = 0
        message_queue = []

        # Subscribe to the topic
        self.consumer.subscribe([self.topic])

        produce_messages(self.producer, self.topic, 2, lamport_time+1, content={"event": "reply"})
        produce_messages(self.producer, self.topic, 3, lamport_time+1, content={"event": "reply"})

        # Alterar para ser uma chamada async
        lamport_time, message_queue = request_critical_section(self.producer, self.consumer, process_id, lamport_time, message_queue)

        # Analisa as variaveis lamport_time e message_queue após a execução da função request_critical_section. 
        self.assertEqual(lamport_time, 5)
        self.assertEqual(len(message_queue), 0)

    def test_request_critical_section_with_more_requests(self):
        process_id = 1
        lamport_time = 0
        message_queue = []

        # Subscribe to the topic
        self.consumer.subscribe([self.topic])

        produce_messages(self.producer, self.topic, 2, lamport_time+1, content={"event": "request"})
        produce_messages(self.producer, self.topic, 3, lamport_time+2, content={"event": "request"})
        produce_messages(self.producer, self.topic, 2, lamport_time+3, content={"event": "reply"})
        produce_messages(self.producer, self.topic, 3, lamport_time+4, content={"event": "reply"})

        # Alterar para ser uma chamada async
        lamport_time, message_queue = request_critical_section(self.producer, self.consumer, process_id, lamport_time, message_queue)

        # Analisa as variaveis lamport_time e message_queue após a execução da função request_critical_section. 
        self.assertEqual(lamport_time, 9)

        expected_queue = [{"lamport_time": 2, "process_id": 2}, {"lamport_time": 3, "process_id": 3}]
        assert expected_queue == message_queue


if __name__ == "__main__":
    unittest.main()