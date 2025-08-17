#!/usr/bin/env python3
"""
Test script to verify the MVP setup
"""
import json
import time
import os
from kafka import KafkaProducer, KafkaConsumer
import requests

def test_kafka_connection():
    """Test Kafka connection and topic creation"""
    print("🔍 Testing Kafka connection...")
    
    broker = os.getenv("KAFKA_BROKER", "localhost:9092")
    
    try:
        # Test producer
        producer = KafkaProducer(
            bootstrap_servers=[broker],
            value_serializer=lambda v: json.dumps(v).encode()
        )
        
        # Send test message
        test_message = {"test": "message", "timestamp": time.time()}
        producer.send("test-topic", test_message)
        producer.flush()
        producer.close()
        
        print("✅ Kafka producer connection successful")
        
        # Test consumer
        consumer = KafkaConsumer(
            "test-topic",
            bootstrap_servers=[broker],
            value_deserializer=lambda m: json.loads(m.decode()),
            auto_offset_reset="earliest",
            consumer_timeout_ms=5000
        )
        
        messages = list(consumer)
        consumer.close()
        
        if messages:
            print("✅ Kafka consumer connection successful")
            return True
        else:
            print("❌ No messages received from Kafka")
            return False
            
    except Exception as e:
        print(f"❌ Kafka connection failed: {e}")
        return False

def test_flink_ui():
    """Test Flink UI accessibility"""
    print("🔍 Testing Flink UI...")
    
    try:
        response = requests.get("http://localhost:8081/overview", timeout=5)
        if response.status_code == 200:
            print("✅ Flink UI is accessible")
            return True
        else:
            print(f"❌ Flink UI returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Flink UI test failed: {e}")
        return False

def test_streamlit_dashboard():
    """Test Streamlit dashboard accessibility"""
    print("🔍 Testing Streamlit dashboard...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit dashboard is accessible")
            return True
        else:
            print(f"❌ Streamlit dashboard returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Streamlit dashboard test failed: {e}")
        return False

def test_data_pipeline():
    """Test the complete data pipeline"""
    print("🔍 Testing data pipeline...")
    
    broker = os.getenv("KAFKA_BROKER", "localhost:9092")
    
    try:
        # Send a test event to the logs topic
        producer = KafkaProducer(
            bootstrap_servers=[broker],
            value_serializer=lambda v: json.dumps(v).encode()
        )
        
        test_event = {
            "ts": "2024-01-01T12:00:00.000Z",
            "user_id": "test-user",
            "campaign_id": "test-campaign",
            "channel": "test-channel",
            "event": "click",
            "cost": 1.0
        }
        
        producer.send("logs", test_event)
        producer.flush()
        producer.close()
        
        print("✅ Test event sent to logs topic")
        
        # Wait a bit for processing
        time.sleep(5)
        
        # Check if processed data appears in results topic
        consumer = KafkaConsumer(
            "results",
            bootstrap_servers=[broker],
            value_deserializer=lambda m: json.loads(m.decode()),
            auto_offset_reset="latest",
            consumer_timeout_ms=10000
        )
        
        messages = list(consumer)
        consumer.close()
        
        if messages:
            print("✅ Data pipeline is working - processed events found in results topic")
            print(f"   Found {len(messages)} processed events")
            return True
        else:
            print("❌ No processed events found in results topic")
            return False
            
    except Exception as e:
        print(f"❌ Data pipeline test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running MVP Setup Tests")
    print("==========================")
    
    tests = [
        ("Kafka Connection", test_kafka_connection),
        ("Flink UI", test_flink_ui),
        ("Streamlit Dashboard", test_streamlit_dashboard),
        ("Data Pipeline", test_data_pipeline)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("======================")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your MVP is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        print("💡 Try running: docker-compose logs -f")

if __name__ == "__main__":
    main()
