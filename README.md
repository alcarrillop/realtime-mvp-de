# Real-time Marketing Analytics MVP

This MVP demonstrates an end-to-end real-time data pipeline using Python, Kafka (via Redpanda), Flink, and Streamlit. It simulates a real-world marketing analytics use case where streaming data is ingested, processed, and visualized continuously.

## Architecture

```
Producer → Kafka (Redpanda) → Flink → Kafka → Streamlit Dashboard
```

### Components

1. **Producer**: Python script that generates synthetic marketing events (impressions, clicks, conversions)
2. **Kafka/Redpanda**: Message broker that ensures durability and fault tolerance
3. **Flink**: Stream processing engine that aggregates metrics in real-time
4. **Streamlit Dashboard**: Real-time visualization of marketing analytics

## Features

- **Real-time Event Generation**: Synthetic marketing events with realistic distributions
- **Stream Processing**: 1-minute window aggregations by campaign and channel
- **Live Dashboard**: Auto-refreshing metrics and visualizations
- **Fault Tolerance**: Kafka ensures no data loss during processing
- **Scalable Architecture**: Each component can be scaled independently

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Running the MVP

1. **Start all services**:
   ```bash
   docker compose up -d
   ```

2. **Access the dashboard**:
   Open http://localhost:8503 in your browser

3. **Monitor the pipeline**:
   - Producer logs: `docker compose logs -f producer`
   - Flink job logs: `docker compose logs -f flink-job`
   - Dashboard logs: `docker compose logs -f dashboard`

### Services

- **Redpanda**: http://localhost:9092 (Kafka API)
- **Streamlit Dashboard**: http://localhost:8503 (Analytics dashboard)

## Data Flow

### 1. Event Generation
The producer generates synthetic marketing events:
```json
{
  "ts": "2024-01-01T12:00:00.000Z",
  "user_id": "uuid",
  "campaign_id": "spring_sale",
  "channel": "google_ads",
  "event": "click",
  "cost": 0.75
}
```

### 2. Stream Processing
Flink processes events in 1-minute windows:
- Groups by campaign and channel
- Aggregates clicks, conversions, and spend
- Calculates CPC and CPA metrics

### 3. Real-time Visualization
The dashboard displays:
- Live metrics (clicks, conversions, spend)
- Campaign performance charts
- Channel analysis
- Top performing campaigns

## Development

### Local Development Setup

1. **Install dependencies**:
   ```bash
   pip install uv
   uv pip install -e .
   ```

2. **Start Kafka/Redpanda**:
   ```bash
   docker compose up redpanda -d
   ```

3. **Run components individually**:
   ```bash
   # Producer
   python -m realtime_mvp.producer.producer
   
   # Dashboard
   streamlit run src/realtime_mvp/dashboard/app.py
   ```

### Project Structure

```
realtime-mvp/
├── docker-compose.yml          # Service orchestration
├── Dockerfile.producer         # Producer container
├── Dockerfile.flink           # Flink job container
├── Dockerfile.dashboard       # Dashboard container
├── src/realtime_mvp/
│   ├── producer/
│   │   └── producer.py        # Event generator
│   ├── flink/
│   │   └── flink_job.py       # Stream processing
│   └── dashboard/
│       └── app.py             # Streamlit dashboard
└── pyproject.toml             # Python dependencies
```

## Configuration

### Environment Variables

- `KAFKA_BROKER`: Kafka broker address (default: localhost:9092)
- `FLINK_HOME`: Flink installation directory
- `PYTHONPATH`: Python module path

### Kafka Topics

- `logs`: Raw marketing events from producer
- `results`: Aggregated metrics from Flink

## Monitoring

### Flink Job Monitoring
- Access Flink UI at http://localhost:8081
- Monitor job status, metrics, and logs
- View processing throughput and latency

### Kafka Monitoring
- Use Redpanda Console for topic monitoring
- Check message rates and consumer lag
- Monitor topic partitions and replicas

## Troubleshooting

### Common Issues

1. **Dashboard shows no data**:
   - Check if Flink job is running: `docker compose logs flink-job`
   - Verify Kafka topics exist: `docker compose exec redpanda rpk topic list`
   - Check producer is generating events: `docker compose logs producer`

2. **Flink job fails to start**:
   - Ensure Java 11+ is available
   - Check Kafka connectivity
   - Verify topic names match

3. **Producer connection issues**:
   - Check Redpanda is running: `docker compose ps`
   - Verify broker address in environment variables
   - Check network connectivity

### Logs

View logs for specific services:
```bash
# All services
docker compose logs

# Specific service
docker compose logs producer
docker compose logs flink-job
docker compose logs dashboard
```

## Performance

### Expected Metrics

- **Event Rate**: ~10-20 events/second from producer
- **Processing Latency**: <1 second end-to-end
- **Dashboard Refresh**: Every 10 seconds
- **Window Size**: 1-minute aggregations

### Scaling

- **Producer**: Can run multiple instances
- **Flink**: Increase parallelism in docker-compose.yml
- **Kafka**: Add more partitions to topics
- **Dashboard**: Can run multiple instances behind load balancer

## Future Enhancements

- Add more event types (purchases, refunds, etc.)
- Implement more complex aggregations
- Add alerting and anomaly detection
- Support for multiple data sources
- Enhanced visualizations and dashboards
- Integration with external marketing platforms

## License

MIT License - see LICENSE file for details.
