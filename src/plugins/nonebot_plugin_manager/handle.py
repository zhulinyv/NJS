from argparse import Namespace

from .plugin import *


class Handle:
    @classmethod
    def ls(cls, args: Namespace) -> str:
        message = ""

        if args.store:
            if not args.is_superuser:
                return "获取插件商店需要超级用户权限！"
            message = "插件商店：\n"
            plugin = get_store_plugin_list()
        else:
            if args.conv["group"]:
                args.conv["user"] = []
            elif args.is_superuser:
                args.conv["user"] = []

            if args.user or args.group:
                if args.is_superuser:
                    args.conv = {"user": args.user, "group": args.group}
                else:
                    return "获取指定会话的插件列表需要超级用户权限！"

            for t in args.conv:
                for i in args.conv[t]:
                    message = f"{'用户' if t == 'user' else '群'} {i} 的插件列表：\n"

            plugin = plugin_manager.get_plugin(args.conv, 1)
            if not args.all:
                plugin = {
                    p: plugin[p]
                    for p in plugin
                    if plugin_manager.get_plugin(args.conv, 4)[p]
                }

        message = message + "\n".join(
            f"[{'o' if plugin[p] else 'x'}] {p}" for p in plugin
        )
        return message

    @classmethod
    def info(cls, args: Namespace) -> str:
        if not args.is_superuser:
            return "获取插件信息需要超级用户权限！"
        return get_plugin_info(args.plugin)

    @classmethod
    def chmod(cls, args: Namespace) -> str:
        if not args.is_superuser:
            return "设置插件权限需要超级用户权限！"
        plugin = plugin_manager.get_plugin()

        if args.all:
            args.plugin = list(plugin.keys())
        if args.reverse:
            args.plugin = list(filter(lambda p: p not in args.plugin, plugin))

        # TODO 这里之后应该有个将 r w x 翻译成 4 2 1 的处理
        result = plugin_manager.chmod_plugin(args.plugin, args.mode)

        return "\n".join(
            f"插件 {p} 的权限成功设置为 {args.mode}！" if result[p] else f"插件 {p} 不存在！"
            for p in result
        )

    @classmethod
    def block(cls, args: Namespace) -> str:
        if args.is_superuser:
            plugin = plugin_manager.get_plugin(perm=6)
        else:
            plugin = plugin_manager.get_plugin(conv=args.conv, perm=6)

        if args.conv["group"]:
            if not args.is_admin and not args.is_superuser:
                return "管理群插件需要群管理员权限！"
            args.conv["user"] = []

        if args.all:
            args.plugin = list(plugin.keys())
        if args.reverse:
            args.plugin = list(filter(lambda p: p not in args.plugin, plugin))

        result = {}
        for p in plugin:
            if p in args.plugin and not plugin[p]:
                args.plugin.remove(p)
                result[p] = False

        if args.user or args.group:
            if args.is_superuser:
                args.conv = {"user": args.user, "group": args.group}
            else:
                return "管理指定会话的插件需要超级用户权限！"

        result.update(plugin_manager.block_plugin(args.plugin, args.conv))

        message = ""
        for t in args.conv:
            if args.conv[t]:
                message += "用户 " if t == "user" else "群 "
                message += ",".join(str(i) for i in args.conv[t])
        message += " 中："

        for plugin, value in result.items():
            message += "\n"
            if value:
                message += f"插件 {plugin} 禁用成功！"
            else:
                message += f"插件 {plugin} 不存在或已关闭编辑权限！"
        return message

    @classmethod
    def unblock(cls, args: Namespace) -> str:
        if args.is_superuser:
            plugin = plugin_manager.get_plugin(perm=6)
        else:
            plugin = plugin_manager.get_plugin(conv=args.conv, perm=6)

        if args.conv["group"]:
            if not args.is_admin and not args.is_superuser:
                return "管理群插件需要群管理员权限！"
            args.conv["user"] = []

        if args.all:
            args.plugin = list(plugin.keys())
        if args.reverse:
            args.plugin = list(filter(lambda p: p not in args.plugin, plugin))

        result = {}
        for p in plugin:
            if p in args.plugin and not plugin[p]:
                args.plugin.remove(p)
                result[p] = False

        if args.user or args.group:
            if args.is_superuser:
                args.conv = {"user": args.user, "group": args.group}
            else:
                return "管理指定会话的插件需要超级用户权限！"

        result.update(plugin_manager.unblock_plugin(args.plugin, args.conv))

        message = ""
        for t in args.conv:
            if args.conv[t]:
                message += "用户" if t == "user" else "群"
                message += ",".join(str(i) for i in args.conv[t])
        message += "中："

        for plugin, value in result.items():
            message += "\n"
            if value:
                message += f"插件 {plugin} 启用成功！"
            else:
                message += f"插件 {plugin} 不存在或已关闭编辑权限！"
        return message

    # 以下功能尚未实现

    @classmethod
    def install(cls, args: Namespace) -> str:
        return ""

    @classmethod
    def uninstall(cls, args: Namespace) -> str:
        return ""
