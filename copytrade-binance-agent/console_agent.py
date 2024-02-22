import aioconsole
from classes.interfaces import *


class ConsoleAgent:

	def __init__(self, trade_agent: TradeAgentInterface):
		self.trade_agent = trade_agent

	async def start(self):
		while True:
			input = await aioconsole.ainput("")
			if input == "":
				command = await aioconsole.ainput("(P)ause, (Q)uit: ")
				if command == "p":
					await self.trade_agent.change_status(AgentStatus.PAUSE)
				elif command == "q":
					await self.trade_agent.change_status(AgentStatus.QUIT)
					break
