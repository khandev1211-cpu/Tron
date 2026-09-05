import redis
try:
    r = redis.Redis(host='localhost', port=6379)
    r.ping()
    print("Redis is running and accessible!")
except Exception as e:
    print(f"Redis connection failed: {e}")
