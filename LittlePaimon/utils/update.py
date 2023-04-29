import datetime
import re
from pathlib import Path

import git
from git.exc import InvalidGitRepositoryError, GitCommandError
from nonebot.utils import run_sync

from . import __version__, NICKNAME
from .requests import aiorequests
from .logger import logger


async def check_update():
    resp = await aiorequests.get('https://api.github.com/repos/zhulinyv/NJS/commits')
    data = resp.json()
    if not isinstance(data, list):
        return '检查更新失败，可能是网络问题，请稍后再试'
    try:
        repo = git.Repo(Path().absolute())
    except InvalidGitRepositoryError:
        return '没有发现git仓库，无法通过git检查更新'
    local_commit = repo.head.commit
    remote_commit = []
    for commit in data:
        if str(local_commit) == commit['sha']:
            break
        remote_commit.append(commit)
    if not remote_commit:
        return f'当前已是最新版本：{__version__}'
    result = '检查到更新，日志如下：\n'
    for i, commit in enumerate(remote_commit, start=1):
        time_str = (datetime.datetime.strptime(commit['commit']['committer']['date'],
                                               '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)).strftime(
            '%Y-%m-%d %H:%M:%S')
        result += f'{i}.{time_str}\n' + commit['commit']['message'].replace(":art:","🎨").replace(":zap:","⚡️").replace(":fire:","🔥").replace(":bug:","🐛").replace(":ambulance:","🚑️").replace(":sparkles:","✨").replace(":memo:","📝").replace(":rocket:","🚀").replace(":lipstick:","💄").replace(":tada:","🎉").replace(":white_check_mark:","✅").replace(":lock:","🔒️").replace(":closed_lock_with_key:","🔐").replace(":bookmark:","🔖").replace(":rotating_light:","🚨").replace(":construction:","🚧").replace(":green_heart:","💚").replace(":arrow_down:","⬇️").replace(":arrow_up:","⬆️").replace(":pushpin:","📌").replace(":construction_worker:","👷").replace(":chart_with_upwards_trend:","📈").replace(":recycle:","♻️").replace(":heavy_plus_sign:","➕").replace(":heavy_minus_sign:","➖").replace(":wrench:","🔧").replace(":hammer:","🔨").replace(":globe_with_meridians:","🌐").replace(":pencil2:","✏️").replace(":poop:","💩").replace(":rewind:","⏪️").replace(":twisted_rightwards_arrows:","🔀").replace(":package:","📦️").replace(":alien:","👽️").replace(":truck:","🚚").replace(":page_facing_up:","📄").replace(":boom:","💥").replace(":bento:","🍱").replace(":wheelchair:","♿️").replace(":bulb:","💡").replace(":beers:","🍻").replace(":speech_balloon:","💬").replace(":card_file_box:","🗃️").replace(":loud_sound:","🔊").replace(":mute:","🔇").replace(":busts_in_silhouette:","👥").replace(":children_crossing:","🚸").replace(":building_construction:","🏗️").replace(":iphone:","📱").replace(":clown_face:","🤡").replace(":egg:","🥚").replace(":see_no_evil:","🙈").replace(":camera_flash:","📸").replace(":alembic:","⚗️").replace(":mag:","🔍️").replace(":label:","🏷️").replace(":seedling:","🌱").replace(":triangular_flag_on_post:","🚩").replace(":goal_net:","🥅").replace(":dizzy:","💫").replace(":wastebasket:","🗑️").replace(":passport_control:","🛂").replace(":adhesive_bandage:","🩹").replace(":monocle_face:","🧐").replace(":coffin:","⚰️").replace(":test_tube:","🧪").replace(":necktie:","👔").replace(":stethoscope:","🩺").replace(":bricks:","🧱").replace(":technologist:","🧑‍💻").replace(":money_with_wings:","💸").replace(":thread:","🧵").replace(":safety_vest:", "🦺") + '\n'
    return result


@run_sync
def update():
    try:
        repo = git.Repo(Path().absolute())
    except InvalidGitRepositoryError:
        return '没有发现git仓库，无法通过git更新，请手动下载最新版本的文件进行替换。'
    logger.info('脑积水更新', '开始执行<m>git pull</m>更新操作')
    origin = repo.remotes.origin
    try:
        origin.pull()
        msg = f'更新完成，版本：{__version__}\n最新更新日志为：\n{repo.head.commit.message.replace(":art:","🎨").replace(":zap:","⚡️").replace(":fire:","🔥").replace(":bug:","🐛").replace(":ambulance:","🚑️").replace(":sparkles:","✨").replace(":memo:","📝").replace(":rocket:","🚀").replace(":lipstick:","💄").replace(":tada:","🎉").replace(":white_check_mark:","✅").replace(":lock:","🔒️").replace(":closed_lock_with_key:","🔐").replace(":bookmark:","🔖").replace(":rotating_light:","🚨").replace(":construction:","🚧").replace(":green_heart:","💚").replace(":arrow_down:","⬇️").replace(":arrow_up:","⬆️").replace(":pushpin:","📌").replace(":construction_worker:","👷").replace(":chart_with_upwards_trend:","📈").replace(":recycle:","♻️").replace(":heavy_plus_sign:","➕").replace(":heavy_minus_sign:","➖").replace(":wrench:","🔧").replace(":hammer:","🔨").replace(":globe_with_meridians:","🌐").replace(":pencil2:","✏️").replace(":poop:","💩").replace(":rewind:","⏪️").replace(":twisted_rightwards_arrows:","🔀").replace(":package:","📦️").replace(":alien:","👽️").replace(":truck:","🚚").replace(":page_facing_up:","📄").replace(":boom:","💥").replace(":bento:","🍱").replace(":wheelchair:","♿️").replace(":bulb:","💡").replace(":beers:","🍻").replace(":speech_balloon:","💬").replace(":card_file_box:","🗃️").replace(":loud_sound:","🔊").replace(":mute:","🔇").replace(":busts_in_silhouette:","👥").replace(":children_crossing:","🚸").replace(":building_construction:","🏗️").replace(":iphone:","📱").replace(":clown_face:","🤡").replace(":egg:","🥚").replace(":see_no_evil:","🙈").replace(":camera_flash:","📸").replace(":alembic:","⚗️").replace(":mag:","🔍️").replace(":label:","🏷️").replace(":seedling:","🌱").replace(":triangular_flag_on_post:","🚩").replace(":goal_net:","🥅").replace(":dizzy:","💫").replace(":wastebasket:","🗑️").replace(":passport_control:","🛂").replace(":adhesive_bandage:","🩹").replace(":monocle_face:","🧐").replace(":coffin:","⚰️").replace(":test_tube:","🧪").replace(":necktie:","👔").replace(":stethoscope:","🩺").replace(":bricks:","🧱").replace(":technologist:","🧑‍💻").replace(":money_with_wings:","💸").replace(":thread:","🧵").replace(":safety_vest:", "🦺")}\n可使用命令[@bot 重启]重启{NICKNAME}'
    except GitCommandError as e:
        if 'timeout' in e.stderr or 'unable to access' in e.stderr:
            msg = '更新失败，连接git仓库超时，请重试或修改源为代理源后再重试。'
        elif 'Your local changes' in e.stderr:
            pyproject_file = Path().parent / 'pyproject.toml'
            pyproject_raw_content = pyproject_file.read_text(encoding='utf-8')
            if raw_plugins_load := re.search(r'^plugins = \[.+]$', pyproject_raw_content, flags=re.M):
                pyproject_new_content = pyproject_raw_content.replace(raw_plugins_load.group(), 'plugins = []')
                logger.info('脑积水更新', f'检测到已安装插件：{raw_plugins_load.group()}，暂时重置')
            else:
                pyproject_new_content = pyproject_raw_content
            pyproject_file.write_text(pyproject_new_content, encoding='utf-8')
            try:
                origin.pull()
                msg = f'更新完成，版本：{__version__}\n最新更新日志为：\n{repo.head.commit.message.replace(":art:","🎨").replace(":zap:","⚡️").replace(":fire:","🔥").replace(":bug:","🐛").replace(":ambulance:","🚑️").replace(":sparkles:","✨").replace(":memo:","📝").replace(":rocket:","🚀").replace(":lipstick:","💄").replace(":tada:","🎉").replace(":white_check_mark:","✅").replace(":lock:","🔒️").replace(":closed_lock_with_key:","🔐").replace(":bookmark:","🔖").replace(":rotating_light:","🚨").replace(":construction:","🚧").replace(":green_heart:","💚").replace(":arrow_down:","⬇️").replace(":arrow_up:","⬆️").replace(":pushpin:","📌").replace(":construction_worker:","👷").replace(":chart_with_upwards_trend:","📈").replace(":recycle:","♻️").replace(":heavy_plus_sign:","➕").replace(":heavy_minus_sign:","➖").replace(":wrench:","🔧").replace(":hammer:","🔨").replace(":globe_with_meridians:","🌐").replace(":pencil2:","✏️").replace(":poop:","💩").replace(":rewind:","⏪️").replace(":twisted_rightwards_arrows:","🔀").replace(":package:","📦️").replace(":alien:","👽️").replace(":truck:","🚚").replace(":page_facing_up:","📄").replace(":boom:","💥").replace(":bento:","🍱").replace(":wheelchair:","♿️").replace(":bulb:","💡").replace(":beers:","🍻").replace(":speech_balloon:","💬").replace(":card_file_box:","🗃️").replace(":loud_sound:","🔊").replace(":mute:","🔇").replace(":busts_in_silhouette:","👥").replace(":children_crossing:","🚸").replace(":building_construction:","🏗️").replace(":iphone:","📱").replace(":clown_face:","🤡").replace(":egg:","🥚").replace(":see_no_evil:","🙈").replace(":camera_flash:","📸").replace(":alembic:","⚗️").replace(":mag:","🔍️").replace(":label:","🏷️").replace(":seedling:","🌱").replace(":triangular_flag_on_post:","🚩").replace(":goal_net:","🥅").replace(":dizzy:","💫").replace(":wastebasket:","🗑️").replace(":passport_control:","🛂").replace(":adhesive_bandage:","🩹").replace(":monocle_face:","🧐").replace(":coffin:","⚰️").replace(":test_tube:","🧪").replace(":necktie:","👔").replace(":stethoscope:","🩺").replace(":bricks:","🧱").replace(":technologist:","🧑‍💻").replace(":money_with_wings:","💸").replace(":thread:","🧵").replace(":safety_vest:", "🦺")}\n可使用命令[@bot 重启]重启{NICKNAME}'
            except GitCommandError as e:
                if 'timeout' in e.stderr or 'unable to access' in e.stderr:
                    msg = '更新失败，连接git仓库超时，请重试或修改源为代理源后再重试。'
                elif ' Your local changes' in e.stderr:
                    msg = f'更新失败，本地修改过文件导致冲突，请解决冲突后再更新。\n{e.stderr}'
                else:
                    msg = f'更新失败，错误信息：{e.stderr}，请尝试手动进行更新'
            finally:
                if raw_plugins_load:
                    pyproject_new_content = pyproject_file.read_text(encoding='utf-8')
                    pyproject_new_content = re.sub(r'^plugins = \[.*]$', raw_plugins_load.group(),
                                                   pyproject_new_content)
                    pyproject_new_content = pyproject_new_content.replace('plugins = []', raw_plugins_load.group())
                    pyproject_file.write_text(pyproject_new_content, encoding='utf-8')
                    logger.info('脑积水更新', f'更新结束，还原插件：{raw_plugins_load.group()}')
            return msg
        else:
            msg = f'更新失败，错误信息：{e.stderr}，请尝试手动进行更新'
    return msg
