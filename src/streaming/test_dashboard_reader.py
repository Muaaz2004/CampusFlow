
from src.streaming.dashboard_stream_reader import get_streaming_data


summary, events, metrics = get_streaming_data()

print("\n========== ROUTE-WISE EVENT SUMMARY ==========")
print(summary)

print("\n========== RECENT STREAMING EVENTS ==========")
print(events)

print("\n========== DASHBOARD METRICS ==========")
for key, value in metrics.items():
    print(f"{key}: {value}")
