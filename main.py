import logging
from anyio import run
import uvicorn

from common.server import api

import endpoints.telegram

logger = logging.getLogger()

class FastAPIServer:
    def __init__(self):
        logger.info("Starting the FastAPI server")

    def run(self):
        uvicorn.run(api, host="127.0.0.1", port=8001)

def main():
    server = FastAPIServer()
    server.run()

if __name__ == "__main__":
    main()