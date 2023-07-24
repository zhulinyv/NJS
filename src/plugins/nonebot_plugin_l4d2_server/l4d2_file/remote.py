# import asyncio
# import paramiko


# class SSHClient:
#     def __init__(self, hostname, port, username, password):
#         self._hostname = hostname
#         self._port = port
#         self._username = username
#         self._password = password
#         self._ssh = None

#     async def connect(self):
#         self._ssh = paramiko.SSHClient()
#         self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         await asyncio.get_event_loop().run_in_executor(
#             None,
#             self._ssh.connect,
#             self._hostname,
#             self._port,
#             self._username,
#             self._password,
#         )

#     async def upload(self, local_file_path, remote_file_path):
#         with paramiko.Transport((self._hostname, self._port)) as transport:
#             await asyncio.get_event_loop().run_in_executor(
#                 None, transport.connect, None, self._username, self._password
#             )
#             sftp = paramiko.SFTPClient.from_transport(transport)
#             await asyncio.get_event_loop().run_in_executor(
#                 None, sftp.put, local_file_path, remote_file_path
#             )

#     async def delete(self, remote_file_path):
#         with paramiko.Transport((self._hostname, self._port)) as transport:
#             await asyncio.get_event_loop().run_in_executor(
#                 None, transport.connect, None, self._username, self._password
#             )
#             sftp = paramiko.SFTPClient.from_transport(transport)
#             await asyncio.get_event_loop().run_in_executor(
#                 None, sftp.remove, remote_file_path
#             )

#     async def read(self, remote_dir_path):
#         with paramiko.Transport((self._hostname, self._port)) as transport:
#             await asyncio.get_event_loop().run_in_executor(
#                 None, transport.connect, None, self._username, self._password
#             )
#             sftp = paramiko.SFTPClient.from_transport(transport)
#             return await asyncio.get_event_loop().run_in_executor(
#                 None, sftp.listdir, remote_dir_path
#             )

#     async def close(self):
#         if self._ssh is not None:
# self._ssh.close()


# async def main():
#     ssh = SSHClient("example.com", 22, "username", "password")
#     await ssh.connect()

#     await ssh.upload("/path/to/local/file", "/path/to/remote/file")
#     await ssh.delete("/path/to/remote/file")
#     files = await ssh.list("/path/to/remote/directory")
#     print(files)

#     await ssh.close()

# if __name__ == '__main__':
#     asyncio.run(main())


# async def remote(
#     mode: str, host, user, password, local_path="", port=22, remote_path=""
# ):
#     """mode:upload、read、del"""
#     client = SSHClient(host, port, user, password)
#     if mode == "upload":
#         await client.upload(local_path, remote_path)
#     elif mode == "read":
#         file = await client.read(remote_path)
#         return file
#     elif mode == "del":
#         await client.delete(remote_path)
