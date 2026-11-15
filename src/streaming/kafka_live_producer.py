
import json
import time
from pathlib import Path
from kafka import KafkaProducer

# ----------------------------------------
# CONFIGURATION
# ----------------------------------------

KAFKA_SERVER = "localhost:9092"
TOPIC = "shuttle-events"

DATA_FILE = Path("data/raw/boarding_events.jsonl")

DELAY_SECONDS = 1.5

# Set to None to process the complete file.
MAX_EVENTS = 30

# ----------------------------------------
# CREATE KAFKA PRODUCER
# ----------------------------------------

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value: json.dumps(
        value
    ).encode("utf-8")
)

print("\n========== CAMPUSFLOW LIVE PRODUCER ==========")

print("Kafka server:", KAFKA_SERVER)
print("Topic:", TOPIC)

# ----------------------------------------
# READ AND PUBLISH EVENTS
# ----------------------------------------

sent_count = 0

try:

    with DATA_FILE.open("r", encoding="utf-8") as file:

        for line in file:

            if MAX_EVENTS is not None and sent_count >= MAX_EVENTS:
                break

            if not line.strip():
                continue

            event = json.loads(line)

            # Give each live replay a unique ID.
            original_id = event.get("event_id", "UNKNOWN")

            event["event_id"] = (
                f"LIVE-{int(time.time() * 1000)}-{original_id}"
            )

            # Publish to Kafka
            future = producer.send(
                TOPIC,
                value=event
            )

            metadata = future.get(timeout=30)

            sent_count += 1

            print(
                f"Event {sent_count} | "
                f"ID: {event['event_id']} | "
                f"Route: {event.get('route_id')} | "
                f"Type: {event.get('event_type')} | "
                f"Offset: {metadata.offset}"
            )

            time.sleep(DELAY_SECONDS)

    producer.flush()

    print("\nProducer completed successfully.")
    print("Total events sent:", sent_count)

except KeyboardInterrupt:

    print("\nProducer stopped by user.")

except Exception as error:

    print("\nProducer error:", error)

finally:

    producer.close()
