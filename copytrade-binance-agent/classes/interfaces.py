import enum
from collections import namedtuple

ErrorDescription = namedtuple('ErrorDescription' , 'code text')

class AgentStatus(enum.Enum):
	NONE = 0
	RUN = 1
	PAUSE = 2
	QUIT = 3

class TradeCommandType(enum.Enum):
	OPEN_ORDER = 0
	CLOSE_ORDER = 1
	CLOSE_ALL = 2 # unused yet

class TradeAgentInterface:
	def get_status(self) -> AgentStatus:
		pass

	async def change_status(self, new_status):
		pass

	def get_config(self):
		pass

	def get_license(self):
		pass

	async def execute_command(self, command_type, data):
		pass

	async def proceed_updates(self, updates):
		pass