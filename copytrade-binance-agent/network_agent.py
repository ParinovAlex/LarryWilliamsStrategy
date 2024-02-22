import asyncio
import socketio
from classes.interfaces import *
from classes.settings import *


class NetworkAgent:

    def __init__(self, trade_agent: TradeAgentInterface):
        self.trade_agent = trade_agent
        self.config = None
        self.license = None
        self.sio = socketio.AsyncClient(logger=True, engineio_logger=True)

    async def setup_client(self):
        @self.sio.event
        async def connect():
            logger.debug(f"Connected to server")

        @self.sio.event
        async def disconnect():
            logger.debug(f"Disconnected from server")

        @self.sio.event
        async def connect_error(message):
            logger.error(f"Connection error: {message}")

        @self.sio.event
        async def update_message(data):
            # get updates from server like {'updates': data, 'sid': sid}
            updates_data = data["updates"]
            logger.debug(f"Event: update_message, event data: {updates_data}")
            # logger.debug(pformat(updates_data))

            status = self.trade_agent.get_status()
            if status == AgentStatus.RUN:
                # proceed with updates without awaiting
                loop = asyncio.get_event_loop()
                loop.create_task(self.trade_agent.proceed_updates(updates=updates_data))
            elif status == AgentStatus.PAUSE:
                logger.debug(f"Current status is PAUSE, skip processing updates")
            else:
                logger.debug(f"Current status is {status}, skip processing updates")

            # send accepted response
            return {"data": data, "result": "accepted"}

    '''
    Emit messages to server
    '''

    async def send_command_response_message(self, command_type, command_data, command_result):
        # send data to server with results of browser command execution, like 	{'command_type': command_type.value, 'command': command_data, 'result': command_result}
        data = {'command_type': command_type.value, 'command': command_data, 'command_result': command_result}
        logger.debug(f"Send command response message: {data}")
        await self.sio.emit("command_response_message",
                            data,
                            callback=self.callback_send_command_response_message)

    async def callback_send_command_response_message(self, data):
        # received response from server like {"result": "accepted"}
        response_result = data["result"]
        logger.debug(f"Server response: '{response_result}'")

    '''
    Agent operations
    '''

    async def start_client(self):
        try:
            await self.sio.connect(self.config["server_url"],
                                   headers={"client_id": self.license["client_id"],
                                            "client_key": self.license["client_key"]})
            await self.sio.wait()
        except Exception as e:
            logger.exception(f"Exception: {e}")

    async def start(self):
        self.config = self.trade_agent.get_config()
        self.license = self.trade_agent.get_license()
        await self.setup_client()
        await self.start_client()
