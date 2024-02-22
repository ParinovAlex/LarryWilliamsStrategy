import json
import asyncio
from classes.interfaces import *
from classes.settings import *
from pprint import pformat
from console_agent import ConsoleAgent
from network_agent import NetworkAgent
from binance_agent import BinanceAgent


class TradeAgent(TradeAgentInterface):
    def __init__(self):
        self.status = AgentStatus.NONE
        self.config = None
        self.license = None
        self.binance_agent = BinanceAgent(self)
        self.console_agent = ConsoleAgent(self)
        self.network_agent = NetworkAgent(self)

    # --------------------------------
    # Getters

    def get_status(self) -> AgentStatus:
        return self.status

    def get_config(self):
        return self.config

    def get_license(self):
        return self.license

    async def execute_command(self, command_type, data):
        return await self.binance_agent.execute_command(command_type, data)

    async def proceed_updates(self, updates):
        logger.debug(f"-----")
        logger.debug(f"Proceed with updates: {updates}")

        for data in updates["close"]:
            logger.debug(f"-----")
            logger.debug(f"Execute close command: {data}")
            command_result = await self.execute_command(TradeCommandType.CLOSE_ORDER, data)
            logger.debug(f"Result: {command_result}")
            await self.network_agent.send_command_response_message(TradeCommandType.CLOSE_ORDER, data, command_result)

        for data in updates["open"]:
            logger.debug(f"-----")
            logger.debug(f"Execute open command: {data}")
            command_result = await self.execute_command(TradeCommandType.OPEN_ORDER, data)
            logger.debug(f"Result: {command_result}")
            await self.network_agent.send_command_response_message(TradeCommandType.OPEN_ORDER, data, command_result)

    # --------------------------------

    def load_config(self):
        try:
            with open('config.json', 'r') as json_file:
                data = json_file.read()
            config = json.loads(data)
            if config:
                self.config = config
                logger.debug("Config loaded:")
                logger.debug(pformat(self.config))
                return True
        except FileNotFoundError:
            logger.exception("Config file not found, aborted.")
            return False

    def load_license(self):
        try:
            with open('license.json', 'r') as json_file:
                data = json_file.read()
            license = json.loads(data)
            if license:
                self.license = license
                logger.debug("License loaded:")
                logger.debug(pformat(self.license))
                return True
        except FileNotFoundError:
            logger.exception("License file not found, aborted.")
            return False

    # --------------------------------

    async def change_status(self, new_status):
        if self.status == AgentStatus.RUN and new_status == AgentStatus.PAUSE:
            self.status = AgentStatus.PAUSE
        elif self.status == AgentStatus.PAUSE and new_status == AgentStatus.PAUSE:
            self.status = AgentStatus.RUN
        elif new_status == AgentStatus.QUIT:
            self.status = new_status
            await self.binance_agent.quit()
        else:
            self.status = new_status
        logger.debug(f"Status changed to: {self.status}")

    # --------------------------------

    def start(self):
        self.status = AgentStatus.RUN
        loop = asyncio.get_event_loop()
        try:
            tasks = [
                loop.create_task(self.binance_agent.start()),
                loop.create_task(self.console_agent.start()),
                loop.create_task(self.network_agent.start())
            ]
            loop.run_until_complete(asyncio.wait(tasks))
        except RuntimeError:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()


agent = TradeAgent()
if agent.load_config() and agent.load_license():
    agent.start()
