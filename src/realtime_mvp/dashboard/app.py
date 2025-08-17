import json
import pandas as pd
import streamlit as st
from kafka import KafkaConsumer
import time
import os
from datetime import datetime

st.set_page_config(page_title="Realtime Marketing Analytics", layout="wide")
st.title("🚀 Real-time Marketing Analytics Dashboard")
st.caption("Live metrics from Kafka topic `results`")

# Get Kafka broker from environment variable or use default
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")

def get_kafka_messages():
    """Get messages from Kafka with proper error handling"""
    try:
        consumer = KafkaConsumer(
            "results",
            bootstrap_servers=[KAFKA_BROKER],
            value_deserializer=lambda m: json.loads(m.decode()),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            consumer_timeout_ms=2000
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
if "last_update" not in st.session_state:
    st.session_state["last_update"] = datetime.now()

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    st.info(f"Kafka Broker: {KAFKA_BROKER}")
    
    # Manual refresh button
    if st.button("🔄 Refresh Data"):
        st.session_state["last_update"] = datetime.now()
        st.rerun()
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh (every 10s)", value=True)
    
    # Data management
    st.header("Data Management")
    if st.button("🗑️ Clear Data"):
        st.session_state["data"] = []
        st.rerun()

# Try to get new messages
new_messages, error = get_kafka_messages()

if error:
    st.error(f"❌ Failed to connect to Kafka: {error}")
    st.info("💡 To fix this, ensure:")
    st.info("1. Redpanda/Kafka is running")
    st.info("2. Flink job is processing data")
    st.info("3. Kafka broker address is correct")
else:
    if new_messages:
        st.session_state["data"].extend(new_messages)
        st.success(f"✅ Received {len(new_messages)} new messages!")
        st.session_state["last_update"] = datetime.now()

# Display data
data = st.session_state["data"]
if data:
    df = pd.DataFrame(data)
    
    # Add timestamp for display
    df['display_time'] = datetime.now().strftime("%H:%M:%S")
    
    # Display key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📊 Total Campaigns", len(df["campaign"].unique()))
    with col2:
        st.metric("🖱️ Total Clicks", df["clicks"].sum())
    with col3:
        st.metric("💰 Total Conversions", df["conversions"].sum())
    with col4:
        st.metric("💵 Total Spend", f"${df['spend'].sum():.2f}")
    with col5:
        st.metric("⏰ Last Update", st.session_state["last_update"].strftime("%H:%M:%S"))
    
    # Display recent data and charts
    left, right = st.columns(2)
    with left:
        st.subheader("📈 Recent Results")
        recent_df = df.sort_values("clicks", ascending=False).tail(10)
        st.dataframe(recent_df[["campaign", "channel", "clicks", "conversions", "spend", "CPC", "CPA"]], 
                    use_container_width=True)
    
    with right:
        st.subheader("📊 Clicks by Campaign")
        campaign_clicks = df.groupby("campaign")["clicks"].sum().sort_values(ascending=False)
        st.bar_chart(campaign_clicks)
    
    # Performance metrics
    st.subheader("📊 Performance Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💰 Cost Per Click (CPC)")
        cpc_data = df.groupby("campaign")["CPC"].mean().sort_values(ascending=False)
        st.bar_chart(cpc_data)
    
    with col2:
        st.subheader("🎯 Cost Per Acquisition (CPA)")
        cpa_data = df.groupby("campaign")["CPA"].mean().sort_values(ascending=False)
        st.bar_chart(cpa_data)
    
    # Channel performance
    st.subheader("📺 Channel Performance")
    channel_metrics = df.groupby("channel").agg({
        "clicks": "sum",
        "conversions": "sum", 
        "spend": "sum"
    }).round(2)
    st.dataframe(channel_metrics, use_container_width=True)
    
    # Top performing campaigns
    st.subheader("🏆 Top Performing Campaigns")
    top_campaigns = df.groupby("campaign").agg({
        "clicks": "sum",
        "conversions": "sum",
        "spend": "sum"
    }).sort_values("clicks", ascending=False).head(5)
    st.dataframe(top_campaigns, use_container_width=True)
    
else:
    st.info("📊 No data available yet. Make sure:")
    st.info("1. The Flink job is running and processing data")
    st.info("2. The producer is generating events")
    st.info("3. Kafka topics are properly configured")

# Auto-refresh logic
if auto_refresh:
    time.sleep(10)
    st.rerun()
