import os
import json
import time
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, config):
        """
        Initialize the CacheManager with memory, disk, and optional Redis fallback.
        """
        self.memory_cache = {}
        self.ttl = config.get('memory_ttl', 60)
        self.disk_path = config.get('disk_path', 'cache/')
        self.redis = None
        
        os.makedirs(self.disk_path, exist_ok=True)
        
        redis_url = config.get('redis_url')
        if redis_url:
            try:
                import redis
                self.redis = redis.Redis.from_url(redis_url)
                self.redis.ping()
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Falling back to disk/memory caching.")
                self.redis = None

    async def get_or_fetch(self, key, fetch_func, *args, ttl=None):
        """
        Retrieve data from cache or fetch it using the provided async function.
        """
        current_ttl = self.ttl if ttl is None else ttl
        now = time.time()
        
        # 1. Check in-memory cache
        if key in self.memory_cache:
            cache_entry = self.memory_cache[key]
            if now - cache_entry['time'] < current_ttl:
                return cache_entry['data']
                
        # 2. Check Redis cache
        if self.redis:
            try:
                cached_data = self.redis.get(key)
                if cached_data:
                    data = json.loads(cached_data)
                    self.memory_cache[key] = {'data': data, 'time': now}
                    return data
            except Exception as e:
                logger.error(f"Redis fetch error for {key}: {e}")

        # 3. Check Disk cache
        disk_file_path = os.path.join(self.disk_path, f"{key}.json")
        if os.path.exists(disk_file_path):
            try:
                # Only trust disk cache if it's fresh enough.
                age = now - os.path.getmtime(disk_file_path)
                if age < current_ttl:
                    with open(disk_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.memory_cache[key] = {'data': data, 'time': now}
                        return data
            except Exception as e:
                logger.error(f"Disk cache read error for {key}: {e}")

        # 4. Fetch fresh data
        data = await fetch_func(*args)
        
        # 5. Save back to all caches
        self.memory_cache[key] = {'data': data, 'time': now}
        
        try:
            json_data = json.dumps(data)
            
            if self.redis:
                # Store in Redis with expiration
                self.redis.set(key, json_data, ex=int(max(1, current_ttl * 2)))
                
            with open(disk_file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
        except Exception as e:
            logger.error(f"Failed to save cache for {key}: {e}")
            
        return data
