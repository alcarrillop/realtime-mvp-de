import os
import json
import time
import requests
from kafka import KafkaProducer, KafkaConsumer
import threading

class FlinkJobSubmitter:
    """Submit Flink job via REST API"""
    
    def __init__(self):
        self.jobmanager_host = os.getenv("FLINK_JOBMANAGER_HOST", "localhost")
        self.jobmanager_port = os.getenv("FLINK_JOBMANAGER_PORT", "8081")
        self.kafka_broker = os.getenv("KAFKA_BROKER", "localhost:9092")
        self.flink_rest_url = f"http://{self.jobmanager_host}:{self.jobmanager_port}"
        
    def submit_job(self):
        """Submit a simple Flink job via REST API"""
        try:
            # Create a simple Flink job JAR (we'll use a pre-built one or create a minimal one)
            # For now, let's create a simple job that reads from Kafka and writes to Kafka
            
            job_config = {
                "entryClass": "org.apache.flink.streaming.examples.kafka.KafkaStreamingJob",
                "programArgs": f"--bootstrap-server {self.kafka_broker} --input-topic logs --output-topic results",
                "parallelism": 1
            }
            
            # Submit job via REST API
            response = requests.post(
                f"{self.flink_rest_url}/jars/upload",
                files={"jarfile": ("flink-kafka-job.jar", open("flink-kafka-job.jar", "rb"))}
            )
            
            if response.status_code == 200:
                jar_id = response.json()["filename"]
                print(f"JAR uploaded successfully: {jar_id}")
                
                # Submit the job
                job_response = requests.post(
                    f"{self.flink_rest_url}/jars/{jar_id}/run",
                    json=job_config
                )
                
                if job_response.status_code == 200:
                    job_id = job_response.json()["jobid"]
                    print(f"Job submitted successfully: {job_id}")
                    return job_id
                else:
                    print(f"Failed to submit job: {job_response.text}")
                    return None
            else:
                print(f"Failed to upload JAR: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error submitting Flink job: {e}")
            return None

class MockFlinkJob:
    """Mock Flink job that simulates the processing"""
    
    def __init__(self):
        self.broker = os.getenv("KAFKA_BROKER", "localhost:9092")
        self.aggregations = {}
        self.last_emit_time = time.time()
        
        # Initialize Kafka consumer and producer
        self.consumer = KafkaConsumer(
            "logs",
            bootstrap_servers=[self.broker],
            value_deserializer=lambda m: json.loads(m.decode()),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="flink-group"
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=[self.broker],
            value_serializer=lambda v: json.dumps(v).encode()
        )
        
        print(f"Mock Flink Job initialized with broker: {self.broker}")
    
    def process_event(self, event):
        """Process a single event and update aggregations"""
        try:
            campaign = event.get("campaign_id", "unknown")
            channel = event.get("channel", "unknown")
            event_type = event.get("event", "unknown")
            cost = event.get("cost", 0.0)
            
            key = f"{campaign}_{channel}"
            
            if key not in self.aggregations:
                self.aggregations[key] = {
                    "clicks": 0,
                    "conversions": 0,
                    "spend": 0.0
                }
            
            # Update aggregations based on event type
            if event_type == "click":
                self.aggregations[key]["clicks"] += 1
                self.aggregations[key]["spend"] += cost
            elif event_type == "conversion":
                self.aggregations[key]["conversions"] += 1
                self.aggregations[key]["spend"] += cost
            
            print(f"Processed event: {event_type} for {campaign}")
            
        except Exception as e:
            print(f"Error processing event: {e}")
    
    def emit_results(self):
        """Emit aggregated results every 60 seconds"""
        while True:
            try:
                current_time = time.time()
                if current_time - self.last_emit_time >= 60:  # 60 seconds
                    if self.aggregations:
                        for key, metrics in self.aggregations.items():
                            campaign, channel = key.split("_", 1)
                            
                            # Calculate derived metrics
                            cpc = metrics["spend"] / metrics["clicks"] if metrics["clicks"] > 0 else 0
                            cpa = metrics["spend"] / metrics["conversions"] if metrics["conversions"] > 0 else 0
                            
                            result = {
                                "campaign": campaign,
                                "channel": channel,
                                "window": "1m",
                                "clicks": metrics["clicks"],
                                "conversions": metrics["conversions"],
                                "spend": round(metrics["spend"], 2),
                                "CPC": round(cpc, 4),
                                "CPA": round(cpa, 2)
                            }
                            
                            self.producer.send("results", result)
                            print(f"Emitted result: {result}")
                        
                        # Reset aggregations after emitting
                        self.aggregations = {}
                        self.last_emit_time = current_time
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"Error in emit_results: {e}")
                time.sleep(10)
    
    def run(self):
        """Main processing loop"""
        print("Starting Mock Flink job...")
        
        # Start background thread for emitting results
        emit_thread = threading.Thread(target=self.emit_results, daemon=True)
        emit_thread.start()
        
        try:
            for message in self.consumer:
                self.process_event(message.value)
        except KeyboardInterrupt:
            print("Shutting down Mock Flink job...")
        finally:
            self.consumer.close()
            self.producer.close()

def main():
    """Main entry point"""
    print("Starting Flink job...")
    
    # Try to submit a real Flink job first
    submitter = FlinkJobSubmitter()
    job_id = submitter.submit_job()
    
    if job_id:
        print(f"Real Flink job submitted with ID: {job_id}")
        # Monitor the job
        while True:
            time.sleep(10)
    else:
        print("Falling back to mock Flink job...")
        # Fall back to mock implementation
        job = MockFlinkJob()
        job.run()

if __name__ == "__main__":
    main()
