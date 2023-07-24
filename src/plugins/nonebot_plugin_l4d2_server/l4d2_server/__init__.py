import asyncio

from rcon.source.async_rcon import close, communicate
from rcon.source.proto import Packet, Type


async def main(host):
    host = "43.142.178.212"
    port = 40003
    password = "1145149191810"
    encoding = "utf-8"

    # Connect to RCON server

    # Main loop
    while True:
        # Read user input
        command = input("> ")
        if not command:
            break

    # 连接服务器
    reader, writer = await asyncio.open_connection(host, port)
    login = Packet.make_login(password, encoding=encoding)
    response = await communicate(reader, writer, login)

    # 等待 SERVERDATA_AUTH_RESPONSE 数据包
    while response.type != Type.SERVERDATA_AUTH_RESPONSE:
        response = await Packet.aread(reader)

    if response.id == -1:
        await close(writer)
        raise WrongPassword()

    # 循环接收用户输入并发送指令
    while True:
        try:
            command = input("请输入指令：")

        except EOFError:
            break

        if command == "停止":
            break
        # 发送指令

        command = f"say {command}"
        request = Packet.make_command(command, encoding=encoding)
        response = await communicate(reader, writer, request)

        # if response.id != request.id:
        #     raise SessionTimeout()

        print(response.payload.decode(encoding, errors="ignore"))

    # 断开连接
    await close(writer)


class WrongPassword(Exception):
    """Indicates a wrong password."""


class SessionTimeout(Exception):
    """Indicates that the session timed out."""
