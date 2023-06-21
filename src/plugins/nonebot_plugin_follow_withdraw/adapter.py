from typing import Any, Dict, List, TypeVar, Callable, Optional, Awaitable

from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

from .model import FollowMessage
from .config import withdraw_config

T_Bot = TypeVar("T_Bot", bound=Bot)
T_Event = TypeVar("T_Event", bound=Event)

WITHDRAW_RULE_FUNC = Callable[[Event, T_State], Awaitable[bool]]
GET_ORIGIN_FUNC = Callable[[Event], Optional[Dict[str, str]]]
GET_MESSAGE_FUNC = Callable[[Any], Optional[Dict[str, str]]]
WITHDRAW_FUNC = Callable[[T_Bot, FollowMessage], Awaitable[Any]]

_allow_apis: Dict[str, List[str]] = {}
_withdraw_rule: Dict[str, WITHDRAW_RULE_FUNC] = {}
_get_origin_funcs: Dict[str, GET_ORIGIN_FUNC] = {}
_get_message_funcs: Dict[str, GET_MESSAGE_FUNC] = {}
_withdraw_funcs: Dict[str, WITHDRAW_FUNC] = {}


def register_allow_apis(adapter_name: str, apis: List[str]):
    _allow_apis[adapter_name] = apis


def register_withdraw_rule(adapter_name: str):
    def _decorator(func: WITHDRAW_RULE_FUNC):
        _withdraw_rule[adapter_name] = func
        return func

    return _decorator


def register_get_origin_func(adapter_name: str):
    def _decorator(func: GET_ORIGIN_FUNC):
        _get_origin_funcs[adapter_name] = func
        return func

    return _decorator


def register_get_message_func(adapter_name: str):
    def _decorator(func: GET_MESSAGE_FUNC):
        _get_message_funcs[adapter_name] = func
        return func

    return _decorator


def register_withdraw_func(adapter_name: str):
    def _decorator(func: WITHDRAW_FUNC):
        _withdraw_funcs[adapter_name] = func
        return func

    return _decorator


def check_allow_api(adapter_name: str, api: str) -> bool:
    if apis := _allow_apis.get(adapter_name):
        return api in apis
    return False


def get_origin_message(event: Event, adapter_name: str) -> Optional[Dict[str, str]]:
    if func := _get_origin_funcs.get(adapter_name):
        return func(event)


def get_message(result: Any, adapter_name: str) -> Optional[Dict[str, str]]:
    if func := _get_message_funcs.get(adapter_name):
        return func(result)


async def withdraw_message(adapter_name: str, bot: Bot, message: FollowMessage):
    if func := _withdraw_funcs.get(adapter_name):
        logger.opt(colors=True).info(
            f"<y>{adapter_name}</y> 跟随原消息<m>{message.origin_message_id}</m>撤回消息<m>{message.message_id}</m>"
        )
        await func(bot, message)


async def check_event(bot: Bot, event: Event, state: T_State) -> bool:
    if bot.self_id in withdraw_config.follow_withdraw_bot_blacklist:
        return False
    adapter_name = bot.adapter.get_name()
    if adapter_name not in withdraw_config.follow_withdraw_enable_adapters:
        return False
    if func := _withdraw_rule.get(adapter_name):
        return await func(event, state)
    return False
