import json, random, time, uuid
from datetime import datetime
from kafka import KafkaProducer

BROKER = "localhost:9092"
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
    producer = KafkaProducer(bootstrap_servers=[BROKER],
                             value_serializer=lambda v: json.dumps(v).encode())
    print(f"Producer -> {TOPIC} @ {BROKER}")
    while True:
        rec = make_event()
        producer.send(TOPIC, rec)
        print("Sent:", rec)
        time.sleep(random.uniform(0.1, 0.6))

if __name__ == "__main__":
    main()
