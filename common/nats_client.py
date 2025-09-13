import json
import logging
from typing import Dict, Any, Optional

from common.config import NATS_URL

import nats
import anyio

logger = logging.getLogger("nats")

class NATSClient:
    _connection: Optional[nats.NATS] = None
    
    @classmethod
    async def connect(cls):
        if cls._connection is None or not cls._connection.is_connected:
            try:
                cls._connection = await nats.connect(NATS_URL)
                logger.info("Connected to NATS server")
            except Exception as e:
                logger.error(f"Failed to connect to NATS: {e}")
                raise
    
    @classmethod
    async def publish(cls, subject: str, data: Dict[Any, Any]):
        try:
            # Ensure connection
            if not cls._connection or not cls._connection.is_connected:
                await cls.connect()
            
            message = json.dumps(data, default=str)
            await cls._connection.publish(subject, message.encode())
            logger.debug(f"Published to {subject}: {message[:100]}...")
            
        except Exception as e:
            logger.error(f"Failed to publish to {subject}: {e}")
            # raise # webhook should still work even if NATS fails
    
    @classmethod
    async def subscribe(cls, subject: str, callback):
        if not cls._connection or not cls._connection.is_connected:
            await cls.connect()
        
        await cls._connection.subscribe(subject, cb=callback)
        logger.info(f"Subscribed to {subject}")
    
    @classmethod
    async def close(cls):
        if cls._connection and cls._connection.is_connected:
            await cls._connection.close()
            cls._connection = None
            logger.info("NATS connection closed")
    
    @classmethod
    def is_connected(cls) -> bool:
        return cls._connection is not None and cls._connection.is_connected