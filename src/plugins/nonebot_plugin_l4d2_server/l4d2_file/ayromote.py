# import asyncio
# import asyncssh


# class AsyncSSHClient:
#     def __init__(self, host, port, username, password=None, private_key=None):
#         self.host = host
#         self.port = port
#         self.username = username
#         self.password = password
#         self.private_key = private_key

#     async def connect(self):
#         if self.private_key is not None:
#             try:
#                 key = asyncssh.read_private_key(self.private_key)
#             except asyncssh.Error as exc:
#                 raise ValueError(f"Unable to read private key: {exc}")
#         else:
#             key = None

#         self.conn = await asyncssh.connect(
#             self.host,
#             self.port,
#             username=self.username,
#             password=self.password,
#             client_keys=key,
#         )

#     async def upload(self, local_path, remote_path):
#         async with self.conn.sftp() as sftp:
#             await sftp.put(local_path, remote_path)

#     async def delete(self, remote_path):
#         async with self.conn.sftp() as sftp:
#             await sftp.remove(remote_path)

#     async def listdir(self, remote_path):
#         async with self.conn.sftp() as sftp:
#             return await sftp.listdir(remote_path)

#     async def close(self):
#         self.conn.close()


# async def remote(
#     mode: str,
#     host: str,
#     user: str,
#     password: str,
#     local_path="",
#     port=22,
#     remote_path="",
# ):
#     """mode:upload、read、del"""
#     client = AsyncSSHClient(host, port, user, password)
#     await client.connect()
#     if mode == "upload":
#         await client.upload(local_path, remote_path)
#     elif mode == "read":
#         file = await client.read(remote_path)
#         return file
#     elif mode == "del":
#         await client.delete(remote_path)
