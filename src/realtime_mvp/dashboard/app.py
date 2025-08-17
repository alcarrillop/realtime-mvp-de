import json
import pandas as pd
import streamlit as st
from kafka import KafkaConsumer
import time

st.set_page_config(page_title="Realtime MVP", layout="wide")
st.title("Realtime Marketing Analytics")
st.caption("Consuming Kafka topic `results`")

def get_kafka_messages():
    """Get messages from Kafka with proper error handling"""
    try:
        consumer = KafkaConsumer(
            "results",
            bootstrap_servers=["localhost:9092"],  # Try localhost first
            value_deserializer=lambda m: json.loads(m.decode()),
            auto_offset_reset="latest",
            enable_auto_commit=True,
            consumer_timeout_ms=1000
        )
        
        messages = []
        for msg in consumer:
            messages.append(msg.value)
        
        consumer.close()
        return messages, None
        
    except Exception as e:
        return [], str(e)

# Initialize session state
if "data" not in st.session_state:
    st.session_state["data"] = []

# Try to get new messages
new_messages, error = get_kafka_messages()

if error:
    st.error(f"Failed to connect to Kafka: {error}")
    st.info("To fix this, you need to:")
    st.info("1. Start Redpanda/Kafka locally, or")
    st.info("2. Update the bootstrap_servers in the code to match your setup")
else:
    if new_messages:
        st.session_state["data"].extend(new_messages)
        st.success(f"Received {len(new_messages)} new messages!")

# Display data
data = st.session_state["data"]
if data:
    df = pd.DataFrame(data)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Campaigns", len(df["campaign"].unique()))
    with col2:
        st.metric("Total Clicks", df["clicks"].sum())
    with col3:
        st.metric("Total Conversions", df["conversions"].sum())
    with col4:
        st.metric("Total Spend", f"${df['spend'].sum():.2f}")
    
    # Display data
    left, right = st.columns(2)
    with left:
        st.subheader("Recent Results")
        st.dataframe(df.sort_values("clicks", ascending=False).tail(15), use_container_width=True)
    with right:
        st.subheader("Clicks by Campaign")
        st.bar_chart(df.groupby("campaign")["clicks"].sum())
    
    # Additional charts
    st.subheader("Performance Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.line_chart(df.groupby("campaign")["CPC"])
    with col2:
        st.line_chart(df.groupby("campaign")["CPA"])
else:
    st.info("No data available yet. Make sure the Flink job is running and producing data.")
    st.info("You can also run the producer to generate sample data.")

# Add a refresh button
if st.button("Refresh Data"):
    st.rerun()

# Auto-refresh every 10 seconds
st.empty()
time.sleep(10)
st.rerun()
