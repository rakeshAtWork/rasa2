# my_custom_channel.py

import json
from sanic import Blueprint, response
from sanic.request import Request
from sanic.websocket import WebSocketCommonProtocol

from rasa.core.channels.channel import InputChannel, UserMessage, CollectingOutputChannel

class MySocketInput(InputChannel):

    def name(self):
        return "my_socket_channel"

    async def on_message(
        self, 
        websocket: WebSocketCommonProtocol, 
        text: str,
        sender_id: str
    ) -> None:
        collector = CollectingOutputChannel()
        message = UserMessage(text, collector, sender_id)

        await self.on_new_message(message)

        for response in collector.messages:
            await websocket.send(json.dumps(response))

    def blueprint(self, on_new_message):
        custom_webhook = Blueprint("custom_webhook", __name__)

        @custom_webhook.route("/", methods=["GET"])
        async def health(request):
            return response.json({"status": "ok"})

        @custom_webhook.websocket("/websocket")
        async def websocket_endpoint(request: Request, ws: WebSocketCommonProtocol):
            while True:
                text = await ws.recv()
                await self.on_message(ws, text, sender_id="default")

        return custom_webhook
