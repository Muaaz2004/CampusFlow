
import json
import time
from pathlib import Path
from kafka import KafkaProducer

# Project configuration
PROJECT_ROOT = Path(__file__).resolve().parents[2]

EVENT_FILE = PROJECT_ROOT / "data" / "raw" / "boarding_events.jsonl"

KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "shuttle-events"

# Test configuration
MAX_EVENTS = 10
DELAY_SECONDS = 0.5


def create_producer():
    """Create and return a Kafka producer."""

    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],

        # Convert Python dictionary into JSON bytes
        value_serializer=lambda event: json.dumps(event).encode("utf-8"),

        acks="all",
        retries=5
    )

    return producer


def publish_events():
    """Read synthetic events and publish them to Kafka."""

    producer = None
    events_sent = 0

    try:
        # Check whether the dataset exists
        if not EVENT_FILE.exists():
            raise FileNotFoundError(f"Event file not found: {EVENT_FILE}")

        producer = create_producer()

        print("===================================")
        print(" CAMPUSFLOW KAFKA PRODUCER")
        print("===================================")
        print(f"Kafka Server : {KAFKA_SERVER}")
        print(f"Topic        : {TOPIC_NAME}")
        print(f"Event File   : {EVENT_FILE}")
        print("-----------------------------------")

        with open(EVENT_FILE, "r", encoding="utf-8") as file:

            for line in file:

                if events_sent >= MAX_EVENTS:
                    break

                event = json.loads(line)

                # Publish event to Kafka
                future = producer.send(TOPIC_NAME, value=event)

                # Wait for broker acknowledgement
                metadata = future.get(timeout=10)

                events_sent += 1

                print(
                    f"Sent {events_sent}: "
                    f"{event['event_id']} | "
                    f"{event['event_type']} | "
                    f"Partition: {metadata.partition} | "
                    f"Offset: {metadata.offset}"
                )

                time.sleep(DELAY_SECONDS)

        producer.flush()

        print("-----------------------------------")
        print(f"Successfully sent {events_sent} events.")

    except KeyboardInterrupt:
        print("\nProducer interrupted by user.")

    except Exception as error:
        print(f"\nProducer error: {error}")

    finally:
        if producer is not None:
            producer.flush()
            producer.close()
            print("Kafka producer connection closed.")


if __name__ == "__main__":
    publish_events()
