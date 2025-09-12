import logging
from typing import Optional, Dict, Any
import json
import hmac
import hashlib
from datetime import datetime

from common.server import api
from common.mysql import MySQL as db
from common.config import ZOOM_SECRET
from common.nats_client import NATSClient as ns

from fastapi import Request, Header, HTTPException

logger = logging.getLogger("zoom")

@api.post("/webhook/zoom")
@api.post("/webhook/zoom/")
async def zoom_webhook(
    request: Request = None,
    x_zm_signature: Optional[str] = Header(None, alias="x-zm-signature"),
    x_zm_request_timestamp: Optional[str] = Header(None, alias="x-zm-request-timestamp")
):

    try:
        body = await request.body()
        body_str = body.decode('utf-8')
        headers = dict(request.headers)

        try:
            event_data = json.loads(body_str)
            logger.info(f"Received event:\n{json.dumps(event_data, indent=4)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        # URL validation case
        if event_data.get('event') == 'endpoint.url_validation':
            
            plain_token = event_data.get('payload', {}).get('plainToken')
            if plain_token:
                hash_object = hmac.new(
                    ZOOM_SECRET.encode('utf-8'),
                    plain_token.encode('utf-8'),
                    hashlib.sha256
                )
                encrypted_token = hash_object.hexdigest()
                logger.info("Returning validation response with encrypted token")
                return {
                    'plainToken': plain_token,
                    'encryptedToken': encrypted_token
                }
            else:
                logger.error("No plainToken found in validation event")
                raise HTTPException(status_code=400, detail="Missing plainToken in validation event")


        if not x_zm_request_timestamp or not x_zm_signature:
            logger.warning("No request headers")
            raise HTTPException(status_code=403, detail="No signature headers provided")
        
        message = f"v0:{x_zm_request_timestamp}:{body_str}"
        hash_object = hmac.new(
            ZOOM_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        expected_signature = f"v0={hash_object.hexdigest()}"
        if x_zm_signature != expected_signature:
            logger.error("Signature validation failed")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Store and publish to NATS
        query = """
        INSERT INTO raw_events (source, payload)
        VALUES (%s, %s)
        """
        params = ("zoom", json.dumps(event_data))

        event_id = db.execute_insert(query, params)

        await ns.publish(
            "zoom.event",
            {
                "event_id": event_id,
                "timestamp": datetime.now().isoformat()
            }
        )

        logger.info(f"Successfully stored zoom event {event_id}")
        return {"status": "ok", "event_id": event_id}
        
    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error processing zoom webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")