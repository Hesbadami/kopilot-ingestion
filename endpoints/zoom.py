import logging
from typing import Optional
import json

from common.server import api
from common.mysql import MySQL as db
from common.config import TELEGRAM_SECRET

from fastapi import Request, Header, HTTPException

logger = logging.getLogger("zoom")

@api.post("/webhook/zoom")
@api.post("/webhook/zoom/")
async def zoom_webhook(
    request: Request = None,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None, alias="X-Telegram-Bot-Api-Secret-Token")
):

    try:
        body = await request.body()
        headers = dict(request.headers)

        try:
            event_data = json.loads(body.decode('utf-8'))
            logger.info(f"Received event:\n{json.dumps(event_data, indent=4)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON")
        

        if not x_telegram_bot_api_secret_token:
            logger.warning("No Telegram webhook secret provided")
            raise HTTPException(status_code=403, detail="No Telegram secret provided")
        
        if x_telegram_bot_api_secret_token != TELEGRAM_SECRET:
            logger.warning("Telegram secret doesn't match")
            raise HTTPException(status_code=403, detail="Invalid Telegram secret")
        
        # Store and publish to NATS
        query = """
        INSERT INTO raw_events (source, payload)
        VALUES (%s, %s)
        """
        params = ("telegram", update_data)

        event_id = db.execute_insert(query, params)

        logger.info(f"Successfully stored telegram event {event_id}")
        return {"status": "ok", "event_id": event_id}
        
    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error processing telegram webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")