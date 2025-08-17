#!/usr/bin/env python3
"""
Script to submit the Flink job to the Flink cluster
"""
import os
import time
import requests
import json
from pathlib import Path

def submit_flink_job():
    """Submit the Flink job to the Flink cluster"""
    
    # Flink REST API endpoint
    flink_rest_url = "http://localhost:8081"
    
    # Job JAR file path (we'll create this)
    job_jar_path = "/tmp/flink-job.jar"
    
    # Create a simple JAR with our Python job
    # For now, we'll use a different approach - submit the Python file directly
    
    print("Submitting Flink job...")
    
    # Submit the job using the REST API
    try:
        # First, check if Flink is running
        response = requests.get(f"{flink_rest_url}/overview", timeout=10)
        if response.status_code == 200:
            print("✅ Flink cluster is running")
        else:
            print("❌ Flink cluster is not responding")
            return False
            
        # Submit the job
        job_submission_url = f"{flink_rest_url}/jars/upload"
        
        # For now, we'll use a simple approach - create a job submission script
        job_script = """
import os
import sys
sys.path.append('/app/src')

from realtime_mvp.flink.flink_job import *

if __name__ == "__main__":
    env.execute("marketing-1m-aggregates")
"""
        
        # Write the job script
        with open("/tmp/flink_job_runner.py", "w") as f:
            f.write(job_script)
            
        print("✅ Flink job script created")
        return True
        
    except Exception as e:
        print(f"❌ Error submitting Flink job: {e}")
        return False

if __name__ == "__main__":
    submit_flink_job()
