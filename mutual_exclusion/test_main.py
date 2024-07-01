import unittest

from main import remove_from_queue

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

if __name__ == "__main__":
    unittest.main()