from datetime import datetime, timedelta
print((datetime.utcnow() - timedelta(days=30)).isoformat())
