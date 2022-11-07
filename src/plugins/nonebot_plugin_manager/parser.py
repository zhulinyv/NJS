from nonebot.rule import ArgumentParser

npm_parser = ArgumentParser("npm")

npm_subparsers = npm_parser.add_subparsers(dest="handle")

list_parser = npm_subparsers.add_parser("ls", help="show plugin list")
list_group = list_parser.add_mutually_exclusive_group()
list_group.add_argument("-s", "--store", action="store_true")
list_group.add_argument(
    "-u", "--user", action="append", nargs="?", default=[], type=int
)
list_group.add_argument(
    "-g", "--group", action="append", nargs="?", default=[], type=int
)
list_parser.add_argument("-a", "--all", action="store_true")

info_parser = npm_subparsers.add_parser("info", help="show plugin info")
info_parser.add_argument("plugin", help="plugin you want to know about")

chmod_parser = npm_subparsers.add_parser("chmod", help="set plugin mode")
chmod_parser.add_argument("mode", type=str, help="mode you want to set")
chmod_parser.add_argument("plugin", nargs="*", help="plugin you want to set")
chmod_parser.add_argument("-a", "--all", action="store_true")
chmod_parser.add_argument("-r", "--reverse", action="store_true")

block_parser = npm_subparsers.add_parser("block", help="block plugin")
block_parser.add_argument("plugin", nargs="*", help="plugins you want to block")
block_parser.add_argument("-a", "--all", action="store_true")
block_parser.add_argument("-r", "--reverse", action="store_true")
block_parser.add_argument(
    "-u", "--user", action="store", nargs="+", default=[], type=int
)
block_parser.add_argument(
    "-g", "--group", action="store", nargs="+", default=[], type=int
)

unblock_parser = npm_subparsers.add_parser("unblock", help="unblock plugin")
unblock_parser.add_argument("plugin", nargs="*", help="plugins you want to unblock")
unblock_parser.add_argument("-a", "--all", action="store_true")
unblock_parser.add_argument("-r", "--reverse", action="store_true")
unblock_parser.add_argument(
    "-u", "--user", action="store", nargs="+", default=[], type=int
)
unblock_parser.add_argument(
    "-g", "--group", action="store", nargs="+", default=[], type=int
)

# 以下功能尚未实现

install_parser = npm_subparsers.add_parser("install", help="install plugin")
install_parser.add_argument("plugins", nargs="*", help="plugins you want to install")
install_parser.add_argument("-i", "--index", action="store", help="point to a mirror")

uninstall_parser = npm_subparsers.add_parser("uninstall", help="uninstall plugin")
uninstall_parser.add_argument(
    "plugins", nargs="*", help="plugins you want to uninstall"
)
