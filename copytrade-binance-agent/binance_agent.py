import asyncio

from binance_f.exception.binanceapiexception import BinanceApiException
from classes.interfaces import *
from binance_f import RequestClient
from binance_f.model.constant import *
from decimal import Decimal, ROUND_DOWN

SECRET_KEY = ""
API_KEY = ""


class BinanceAgent:

    def __init__(self, trade_agent: TradeAgentInterface):
        self.trade_agent = trade_agent
        self.should_quit = False

    """
    -----------------------------------
    Run modes
    """

    async def start(self):
        while not self.should_quit:
            await asyncio.sleep(1)

    async def init(self, skip_state):
        return

    """
    -----------------------------------
    Trading operations
    """

    def __adjust_quantity(self, coin_name, initial_quantity):
        request_client = RequestClient(api_key=API_KEY, secret_key=SECRET_KEY)
        exchange_infos = request_client.get_exchange_information()
        exchange_info = next((x for x in exchange_infos.symbols if x.baseAsset == coin_name), None)
        if exchange_info is None:
            raise Exception(f"can't identify exchange_info for {coin_name}")

        filter_lot_size = next((x for x in exchange_info.filters if x['filterType'] == 'LOT_SIZE'), None)
        if filter_lot_size is None:
            raise Exception(f"can't find LOT_SIZE filter for founded exchange_info of {coin_name}")
        step_size = Decimal(filter_lot_size['stepSize'])

        step_size_decimal = Decimal(str(step_size))
        quantity = Decimal(str(initial_quantity)).quantize(step_size_decimal, rounding=ROUND_DOWN)
        print(f"Rounded qty {quantity}")
        return float(str(quantity))

    def open_order(self,
                   account_name,
                   coin_name,
                   margin,
                   leverage,
                   stop_loss,
                   take_profit,
                   is_long=True,
                   platform_id="",
                   platform_open_timestamp=0,
                   trader_uid="",
                   trader_name=""):
        request_client = RequestClient(api_key=API_KEY, secret_key=SECRET_KEY)
        margin = self.__adjust_quantity(coin_name=coin_name, initial_quantity=margin)

        if margin == 0:
            order_object = {"id": -1,
                            "platform_id": platform_id,
                            "platform_open_timestamp": platform_open_timestamp,
                            "status": "filled?",
                            "status_code": "stub",
                            "price": "unknown price",
                            "liquidation_price": "unknown_liquidation_price",
                            "timestamp": -1,
                            "trader_uid": trader_uid,
                            "trader_name": trader_name,
                            "qty": margin}

            result = {"success": True,
                      "status": {"code": "ok", "text": ""},
                      "order": order_object}
            return result

        print(f"Open order coin_name={coin_name}, margin={margin}, is_long={is_long}, platform_open_timestamp={platform_open_timestamp}")

        if is_long:
            position_side = PositionSide.LONG
            order_side = OrderSide.BUY
        else:
            position_side = PositionSide.SHORT
            order_side = OrderSide.SELL

        symbol = f"{coin_name}USDT"

        #Try to adjust leverage
        #self.__try_adjust_leverege(symbol=symbol, desired_leverage=int(leverage))

        try:
            binance_result = request_client.post_order(symbol=symbol,
                                               side=order_side,
                                               ordertype=OrderType.MARKET,
                                               quantity=margin,
                                               positionSide=position_side)
        except BinanceApiException as e:
            order_object = {"id": -1,
                            "platform_id": platform_id,
                            "platform_open_timestamp": platform_open_timestamp,
                            "status": f"Binance exception {e.error_code} {e.error_message}",
                            "status_code": "stub",
                            "price": "unknown price",
                            "liquidation_price": "unknown_liquidation_price",
                            "timestamp": -1,
                            "trader_uid": trader_uid,
                            "trader_name": trader_name,
                            "qty": margin}

            result = {"success": True,
                      "status": {"code": "ok", "text": ""},
                      "order": order_object}
            return result

        print("result  >>> ", binance_result)

        response_json = {}
        '''
        order_status_code = str(response_json["data"]["status"]["code"])
        order_status = response_json["data"]["status"]["value"]
        order_price = response_json["data"]["price"]
        order_liquidation_price = response_json["data"]["sysForcePrice"]
        order_id = str(response_json["data"]["orderId"])
        order_timestamp = response_json["timestamp"]
        # print(f"Response: {response_json}")
        order_object = {"id": order_id,
                        "platform_id": platform_id,
                        "platform_open_timestamp": platform_open_timestamp,
                        "status": order_status,
                        "status_code": order_status_code,
                        "price": order_price,
                        "liquidation_price": order_liquidation_price,
                        "timestamp": order_timestamp,
                        "trader_uid": trader_uid,
                        "trader_name": trader_name}
        result = {"success": True,
                  "status": {"code": "ok", "text": ""},
                  "order": order_object}

                        '''
        # logger.debug(pformat(result))
        # return result
        order_object = {"id": binance_result.orderId,
                        "platform_id": platform_id,
                        "platform_open_timestamp": platform_open_timestamp,
                        "status": "filled?",
                        "status_code": "stub",
                        "price": "unknown price",
                        "liquidation_price": "unknown_liquidation_price",
                        "timestamp": binance_result.updateTime,
                        "trader_uid": trader_uid,
                        "trader_name": trader_name,
                        "qty": margin}
        result = self.__open_order_error_result("timeout", "Timeout error", platform_id, platform_open_timestamp,
                                                trader_uid, trader_name)

        result = {"success": True,
                  "status": {"code": "ok", "text": ""},
                  "order": order_object}
        return result

    def __open_order_error_result(self, status_code, status_text, platform_id, platform_open_timestamp, trader_uid,
                                  trader_name):
        order_object = {"id": "",
                        "platform_id": platform_id,
                        "platform_open_timestamp": platform_open_timestamp,
                        "status": "",
                        "status_code": "",
                        "price": 0,
                        "liquidation_price": 0,
                        "timestamp": 0,
                        "trader_uid": trader_uid,
                        "trader_name": trader_name}
        result = {"success": False,
                  "status": {"code": status_code, "text": status_text},
                  "order": order_object}
        return result

    def close_order(self, order_id, coin_name, margin, is_long):
        print(f"Close order order_id={order_id}, coin_name={coin_name}, margin={margin}, is_long={is_long}")

        if order_id == '-1':
            order_object = {"id": order_id,
                            "close_type": "by bot",
                            "status": "uknown status",
                            "status_code": "filled?",
                            "price": "unknown_price",
                            "earnings": -1,
                            "timestamp": 1222}

            result = {"success": True,
                      "status": {"code": "ok", "text": ""},
                      "order": order_object}
            return result

        if is_long:
            position_side = PositionSide.LONG
            order_side = OrderSide.SELL
        else:
            position_side = PositionSide.SHORT
            order_side = OrderSide.BUY

        symbol = f"{coin_name}USDT"  # BNBBTC
        request_client = RequestClient(api_key=API_KEY, secret_key=SECRET_KEY)
        result = request_client.post_order(symbol=symbol,
                                           side=order_side,
                                           ordertype=OrderType.MARKET,
                                           quantity=margin,
                                           positionSide=position_side)
        print(result)

        order_object = {"id": order_id,
                        "close_type": "by bot",
                        "status": "uknown status",
                        "status_code": "filled?",
                        "price": "unknown_price",
                        "earnings": -1,
                        "timestamp": 1222}
        result = self.__close_order_error_result("timeout", "Timeout error", order_id)

        result = {"success": True,
                  "status": {"code": "ok", "text": ""},
                  "order": order_object}
        return result

    def __close_order_error_result(self, status_code, status_text, order_id):
        order_object = {"id": order_id,
                        "close_type": 0,
                        "status": "",
                        "status_code": "",
                        "price": 0,
                        "earnings": 0,
                        "timestamp": 0}
        result = {"success": False,
                  "status": {"code": status_code, "text": status_text},
                  "order": order_object}
        return result

    """
    -----------------------------------
    Utilities
    """

    async def execute_command(self, type, data):
        return self.execute_command_sync(type=type, data=data)

    def execute_command_sync(self, type, data):
        if type == TradeCommandType.OPEN_ORDER:
            return self.open_order(account_name=data["account_name"],
                                   coin_name=data["coin_name"],
                                   margin=data["qty"],
                                   leverage=str(data["leverage"]),
                                   stop_loss=str(data["stop_loss"]),
                                   take_profit=str(data["take_profit"]),
                                   is_long=data["is_long"],
                                   platform_id=data["platform_id"],
                                   platform_open_timestamp=data["platform_open_timestamp"],
                                   trader_uid=data["trader_uid"],
                                   trader_name=data["trader_name"])

        # order_id, coin_name, margin, is_long
        elif type == TradeCommandType.CLOSE_ORDER:
            return self.close_order(order_id=data["order_id"],
                                    coin_name=data["coin_name"],
                                    margin=data["qty"],
                                    is_long=data["is_long"])

    async def quit(self):
        self.should_quit = True

    def __try_adjust_leverege(self, symbol: str, desired_leverage: int):
        request_client = RequestClient(api_key=API_KEY, secret_key=SECRET_KEY)
        try:
            request_client.change_initial_leverage(symbol, desired_leverage)
            return True
        except BinanceApiException as e:
            print(f"errorCode = {e.error_code}, errorMessage = {e.error_message}")
            return False

    def test(self):
        request_client = RequestClient(api_key=API_KEY, secret_key=SECRET_KEY)
        try:
            request_client.change_initial_leverage("BTCUSDT", 1)
        except BinanceApiException as e:
            print(f"errorCode = {e.error_code}, errorMessage = {e.error_message}")
        print("another line")

'''
binance_agent = BinanceAgent(None)

binance_agent.open_order(
    account_name=None,
    coin_name="XRP",
    margin=8.0,
    leverage=None,
    stop_loss=None,
    take_profit=None,
    is_long=False
)
binance_agent.close_order(
    order_id="???",
    coin_name="XRP",
    margin=8.0,
    is_long=False
)
binance_agent.open_order(
    account_name=None,
    coin_name="XRP",
    margin=8.0,
    leverage=None,
    stop_loss=None,
    take_profit=None,
    is_long=True
)
'''

'''
binance_agent.close_order(
    order_id="???",
    coin_name="XRP",
    margin=8.0,
    is_long=True
)
'''
