from pathlib import Path
from typing import List, Union

import git
from git.exc import GitCommandError
from nonebot.log import logger


async def update_from_git(
    level: int = 0,
    repo_path: Union[str, Path, None] = None,
    log_config: dict = {
        "key": "✨🐛🎨⚡🍱♻️",
        "num": 7,
    },
    is_update: bool = True,
) -> List[str]:
    if repo_path is None:
        repo_path = Path(__file__).parents[2]
    repo = git.Repo(repo_path)  # type: ignore
    o = repo.remotes.origin

    if is_update:
        # 清空暂存
        if level >= 2:
            logger.warning("[l4更新] 正在执行 git clean --xdf")
            repo.git.clean("-xdf")
        # 还原上次更改
        if level >= 1:
            logger.warning("[l4更新] 正在执行 git reset --hard")
            repo.git.reset("--hard")

        try:
            pull_log = o.pull()
            logger.info(f"[l4更新] {pull_log}")
        except GitCommandError as e:
            logger.warning(e)
            return []

    commits = list(repo.iter_commits(max_count=40))
    log_list = []
    for commit in commits:
        if isinstance(commit.message, str):
            for key in log_config["key"]:
                if key in commit.message:
                    log_list.append(commit.message.replace("\n", ""))
                    if len(log_list) >= log_config["num"]:
                        break
    return log_list
