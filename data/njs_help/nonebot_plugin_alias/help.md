### 使用

**以下命令需要加[命令前缀](https://v2.nonebot.dev/docs/api/config#Config-command_start) (默认为`/`)，可自行设置为空**

- `alias [别名]=[指令名称]` 添加别名
- `alias [别名]` 查看别名
- `alias -p` 查看所有别名
- `unalias [别名]` 删除别名
- `unalias -a` 删除所有别名

默认只在当前群聊/私聊中生效，使用 `-g` 参数添加全局别名；增删全局别名需要超级用户权限

- `alias -g [别名]=[指令名称]` 添加全局别名
- `unalias -g [别名]` 删除全局别名