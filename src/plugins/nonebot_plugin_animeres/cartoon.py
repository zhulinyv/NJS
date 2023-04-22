from aiohttp import ClientSession, TCPConnector
from nonebot.log import logger
from importlib import __import__
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Generator, overload, Type, Iterable, Sequence, Callable, Awaitable

from .config import global_config, BaseModel, Config

methods: List[Type["BaseMethod"]] = []


try:
    from nonebot.adapters.onebot.v11 import Message
except Exception:
    ...


def add_method(func: Type["BaseMethod"]):
    methods.append(func)


async def GetCartoons(keyword: str) -> Optional["Cartoons"]:
    """获取对应的资源
 
    Returns:
        Cartoons: 资源列表
    """
    for method in methods:
        async with ClientSession(base_url=method.base_url, connector=TCPConnector(ssl=False), trust_env=True) as session:
            try:
                if cartoons := await method(session)(keyword):
                    return cartoons
            except Exception as err:
                logger.error(f"{method.name or method.__name__}获取失败")
                logger.exception(err)
                continue


C_Cartoon = Optional[Callable[["Cartoon"], Awaitable[Optional[str]]]]


class Cartoon(BaseModel):
    """资源"""
    title: str                  # 标题
    tag: str                    # 用于分类的标签
    size: Optional[str] = None  # 大小
    link: Optional[str] = None  # 跳转链接
    magnet: str = ""            # 种子链接
    callable: C_Cartoon = None

    def to_string_callable(self, func: C_Cartoon):
        """to_string的依赖注入

        Args:
            func (Callable[[Cartoon], Awaitable[str]]): 回调函数
        """
        self.callable = func

    async def to_string(self) -> str:
        if self.callable is not None:
            if string := await self.callable(self):
                return string
        return global_config.cartoon_formant.format(**self.dict())


class Cartoons:
    """多个资源"""
    _keys: Optional[List[str]] = None

    def __init__(self, 
                 cartoons: Optional[Union[Sequence[Cartoon], Iterable[Cartoon]]] = None
                 ):
        self.cartoons: List[Cartoon] = []
        self.sort: Dict[str, List[Cartoon]] = {}    # 分类
        self.add(*cartoons or ())

    def __repr__(self) -> str:
        return str(self.cartoons)

    @property
    def keys(self) -> List[str]:
        """资源的全部类型

        Returns:
            List[str]: 资源类型
        """
        if self._keys is None:
            self._keys = list(self.sort.keys())
        return self._keys

    def add(self, *cartoons: Cartoon):
        """添加资源"""
        for cartoon in cartoons:
            self.cartoons.append(cartoon)
            sort = self.sort.get(cartoon.tag)
            if sort is None:    # 当该资源类型不存在时刷新keys
                self._keys = None
                self.sort[cartoon.tag] = []
            self.sort[cartoon.tag].append(cartoon)

    @overload
    def __getitem__(self, value: int) -> Cartoon: ...
    @overload
    def __getitem__(self, value: slice) -> "Cartoons": ...
    def __getitem__(self, value: Union[int, slice]) -> Union[Cartoon, "Cartoons"]:
        if isinstance(value, int):
            return self.cartoons[value]
        return Cartoons(self.cartoons[value])

    def get(self, 
            key: Union[int, str]
            ) -> Optional["Cartoons"]:
        """获取资源

        Returns:
            Cartoons: 多个资源
        """
        try:
            key = self.keys[key] if isinstance(key, int) else key
            return Cartoons(self.sort[key])
        except (IndexError, KeyError):
            return None

    def __iter__(self) -> Generator[Cartoon, None, None]:
        yield from self.cartoons

    async def forward_msg(self, 
                    uin: int, 
                    anime: Optional["Cartoons"] = None,
                    ) -> List[Dict[str, Any]]:
        """合并转发

        Args:
            uin (int): 用户QQ
            anime (Optional[&quot;Cartoons&quot;], optional): 多个资源. Defaults to None.

        Returns:
            List[dict]: 合并转发内容
        """
        return [{
            "type": "node",
            "data": {
                "name": "使用迅雷等bit软件下载",
                "uin": uin,
                "content": Message(await i.to_string())
                }
            } for i in anime or self]
    
    def __bool__(self) -> bool:
        return bool(self.cartoons)


class BaseMethod(ABC):
    name: Optional[str] = None
    base_url: Optional[str] = None
    config: Config = global_config

    @property
    def proxy(self) -> Optional[str]:
        return self.config.cartoon_proxy

    def __init__(self, session: ClientSession): 
        self.session: ClientSession = session

    @abstractmethod
    async def __call__(self, keyword: str) -> Cartoons: ...


from . import functions

