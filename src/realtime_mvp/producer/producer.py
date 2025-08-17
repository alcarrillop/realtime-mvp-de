import json, random, time, uuid, os
from datetime import datetime
from kafka import KafkaProducer

# Get Kafka broker from environment variable or use default
BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = "logs"
EVENTS = ["impression", "click", "conversion"]
CHANNELS = ["google_ads", "facebook_ads", "email", "tiktok"]
CAMPAIGNS = ["spring_sale", "retargeting", "brand_awareness"]

def make_event() -> dict:
    e = random.choices(EVENTS, weights=[80, 17, 3])[0]
    return {
        "ts": datetime.utcnow().isoformat(),
        "user_id": str(uuid.uuid4()),
        "campaign_id": random.choice(CAMPAIGNS),
        "channel": random.choice(CHANNELS),
        "event": e,
        "cost": round(random.uniform(0.2, 1.5), 2) if e == "click" else 0.0,
    }

def main():
    print(f"Starting producer -> {TOPIC} @ {BROKER}")
    
    # Create producer with retry logic
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[BROKER],
                value_serializer=lambda v: json.dumps(v).encode(),
                retries=3,
                acks='all'
            )
            print(f"Connected to Kafka at {BROKER}")
            break
        except Exception as e:
            print(f"Failed to connect to Kafka: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
    
    # Generate and send events
    while True:
        try:
            rec = make_event()
            producer.send(TOPIC, rec)
            print(f"Sent: {rec['event']} for campaign {rec['campaign_id']} via {rec['channel']}")
            time.sleep(random.uniform(0.1, 0.6))
        except Exception as e:
            print(f"Error sending event: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
