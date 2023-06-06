import asyncio
import math
import time
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Literal, cast, overload

from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_htmlrender import get_new_page
from PIL import Image, ImageFilter
from PIL.Image import Resampling
from pil_utils import BuildImage, text2image
from playwright.async_api import Page, ViewportSize

from .config import config
from .resource import RES_CALENDER_BANNER, RES_GRADIENT_BG
from .util import async_req, img_invert_rgba, parse_time_delta

PAGE_KWARGS = {
    "is_mobile": True,
    "viewport": ViewportSize(width=767, height=800),
}


@overload
async def schale_get(suffix: str, raw: Literal[False] = False, **kwargs) -> Any:
    ...


@overload
async def schale_get(suffix: str, raw: Literal[True] = True, **kwargs) -> bytes:
    ...


async def schale_get(suffix, raw=False, **kwargs):
    return await async_req(f"{config.ba_schale_url}{suffix}", raw=raw, **kwargs)  # type: ignore


async def schale_get_stu_data(loc: str = "cn") -> List[Dict[str, Any]]:
    return await schale_get(f"data/{loc}/students.min.json")


async def schale_get_common() -> Dict[str, Any]:
    return await schale_get("data/common.min.json")


async def schale_get_localization(loc: str = "cn") -> Dict[str, Any]:
    return cast(dict, await schale_get(f"data/{loc}/localization.min.json"))


async def schale_get_raids(loc: str = "cn") -> Dict[str, Any]:
    return cast(dict, await schale_get(f"data/{loc}/raids.min.json"))


async def schale_get_stu_dict(key="Name"):
    return {x[key]: x for x in await schale_get_stu_data()}


async def schale_get_stu_info(stu):
    async with cast(Page, get_new_page(**PAGE_KWARGS)) as page:
        await page.goto(
            f"{config.ba_schale_mirror_url}?chara={stu}",
            timeout=60 * 1000,
            wait_until="networkidle",
        )

        # 进度条拉最大
        await page.add_script_tag(content="utilStuSetAllProgressMax();")

        return await page.screenshot(full_page=True)


async def schale_calender(server):
    return MessageSegment.image(
        await schale_get_calender(
            server,
            *(
                await asyncio.gather(
                    schale_get_stu_data(),
                    schale_get_common(),
                    schale_get_localization(),
                    schale_get_raids(),
                )
            ),
        ),
    )


def find_current_event(ev, now=None):
    if not now:
        now = datetime.now()
    for _e in ev:
        _start = datetime.fromtimestamp(_e["start"])
        _end = datetime.fromtimestamp(_e["end"])
        if _start <= now < _end:
            _remain = _end - now
            return _e, _start, _end, _remain
    return None


async def schale_get_calender(server, students, common, localization, raids):
    students = {x["Id"]: x for x in students}

    region = common["regions"][server]
    now = datetime.now()

    pic_bg = BuildImage.new("RGBA", (1400, 640), (255, 255, 255, 70))

    def format_time(_start, _end, _remain):
        dd, hh, mm, ss = parse_time_delta(_remain)
        return (
            f"{_start} ~ {_end} | "
            f"剩余 [b][color=#fc6475]{dd}天 {hh:0>2d}:{mm:0>2d}:{ss:0>2d}[color=#fc6475][/b]"
        )

    async def draw_gacha():
        pic = pic_bg.copy().draw_text(
            (25, 25, 1375, 150),
            "特选招募",
            weight="bold",
            max_fontsize=80,
        )
        c_gacha = region["current_gacha"]
        if r := find_current_event(c_gacha):
            g = r[0]
            t = format_time(*(r[1:]))
            pic = pic.paste(
                ti := text2image(
                    t,
                    (255, 255, 255, 0),
                    fontsize=45,
                    max_width=1350,
                    align="center",
                ),
                (int((1400 - ti.width) / 2), 150),
                True,
            )
            stu = [students[x] for x in g["characters"]]

            async def process_avatar(s):
                return (
                    BuildImage.open(
                        BytesIO(
                            await schale_get(
                                f'images/student/collection/{s["CollectionTexture"]}.webp',
                                raw=True,
                            ),
                        ),
                    )
                    .resize((300, 340))
                    .paste(
                        BuildImage.new("RGBA", (300, 65), (255, 255, 255, 120)),
                        (0, 275),
                        True,
                    )
                    .convert("RGB")
                    .circle_corner(25)
                    .draw_text((0, 275, 300, 340), s["Name"], max_fontsize=50)
                )

            avatars = await asyncio.gather(*[process_avatar(x) for x in stu])
            ava_len = len(avatars)
            x_index = int((1400 - (300 + 25) * ava_len + 25) / 2)

            for p in avatars:
                pic = pic.paste(p, (x_index, 250), True)
                x_index += p.width + 25

            return pic
        return None

    async def draw_event():
        pic = pic_bg.copy().draw_text(
            (25, 25, 1375, 150),
            "当前活动",
            weight="bold",
            max_fontsize=80,
        )
        c_event = region["current_events"]
        if r := find_current_event(c_event):
            g = r[0]
            t = format_time(*(r[1:]))
            pic = pic.paste(
                ti := text2image(
                    t,
                    (255, 255, 255, 0),
                    fontsize=45,
                    max_width=1350,
                    align="center",
                ),
                (int((1400 - ti.width) / 2), 150),
                True,
            )
            ev = g["event"]
            ev_name = ""
            if ev >= 10000:
                ev_name = " (复刻)"
                ev %= 10000
            ev_name = localization["EventName"][str(ev)] + ev_name

            ev_bg, ev_img = await asyncio.gather(
                schale_get(f"images/campaign/Campaign_Event_{ev}_Normal.png", True),
                schale_get(
                    f"images/eventlogo/Event_{ev}_{'Tw' if server else 'Jp'}.png",
                    True,
                ),
            )

            ev_bg = (
                BuildImage.open(BytesIO(ev_bg))
                .convert("RGBA")
                .resize_height(340)
                .filter(ImageFilter.GaussianBlur(3))
            )
            ev_bg = (
                ev_bg.paste(
                    BuildImage.open(BytesIO(ev_img))
                    .convert("RGBA")
                    .resize(
                        (ev_bg.width, ev_bg.height - 65),
                        keep_ratio=True,
                        inside=True,
                        bg_color=(255, 255, 255, 0),
                    ),
                    alpha=True,
                )
                .paste(
                    BuildImage.new("RGBA", (ev_bg.width, 65), (255, 255, 255, 120)),
                    (0, ev_bg.height - 65),
                    True,
                )
                .convert("RGB")
                .circle_corner(25)
                .draw_text(
                    (0, ev_bg.height - 65, ev_bg.width, ev_bg.height),
                    ev_name,
                    max_fontsize=50,
                )
            )
            return pic.paste(ev_bg, (int((pic.width - ev_bg.width) / 2), 250), True)
        return None

    async def draw_raid():
        pic = pic_bg.copy()
        if r := find_current_event(region["current_raid"]):
            ri = r[0]
            t = format_time(*(r[1:]))
            pic = pic.paste(
                ti := text2image(
                    t,
                    (255, 255, 255, 0),
                    fontsize=45,
                    max_width=1350,
                    align="center",
                ),
                (int((1400 - ti.width) / 2), 150),
                True,
            )

            tp = "TimeAttack" if (time_atk := (ri["raid"] >= 1000)) else "Raid"
            raid = {x["Id"]: x for x in raids[tp]}
            c_ri = raid[ri["raid"]]
            pic = pic.draw_text(
                (25, 25, 1375, 150),
                localization["StageType"][tp],
                weight="bold",
                max_fontsize=80,
            )

            if time_atk:
                tk_bg = {
                    "Shooting": "TimeAttack_SlotBG_02",
                    "Defense": "TimeAttack_SlotBG_01",
                    "Destruction": "TimeAttack_SlotBG_03",
                }
                bg_url = f'images/timeattack/{tk_bg[c_ri["DungeonType"]]}'
                fg_url = f'images/enemy/{c_ri["Icon"]}.png'
            else:
                bg_url = f'images/raid/Boss_Portrait_{c_ri["PathName"]}_LobbyBG'
                if len(c_ri["Terrain"]) > 1 and ri["terrain"] == c_ri["Terrain"][1]:
                    bg_url += f'_{ri["terrain"]}'
                fg_url = f'images/raid/Boss_Portrait_{c_ri["PathName"]}_Lobby.png'
            bg_url += ".png"
            terrain = c_ri["Terrain"] if time_atk else ri["terrain"]

            color_map = {
                "LightArmor": (167, 12, 25),
                "Explosion": (167, 12, 25),
                "HeavyArmor": (178, 109, 31),
                "Pierce": (178, 109, 31),
                "Unarmed": (33, 111, 156),
                "Mystic": (33, 111, 156),
                "Normal": (115, 115, 115),
            }
            atk_color = color_map[
                c_ri["BulletType" if time_atk else "BulletTypeInsane"]
            ]
            def_color = color_map[c_ri["ArmorType"]]

            c_bg, c_fg, icon_def, icon_atk, icon_tr = await asyncio.gather(
                *[
                    schale_get(bg_url, True),
                    schale_get(fg_url, True),
                    schale_get("images/ui/Type_Defense_s.png", True),
                    schale_get("images/ui/Type_Attack_s.png", True),
                    schale_get(f"images/ui/Terrain_{terrain}.png", True),
                ],
            )

            icon_def = (
                BuildImage.new("RGBA", (64, 64), def_color)
                .paste(
                    BuildImage.open(BytesIO(icon_def))
                    .convert("RGBA")
                    .resize_height(48),
                    (8, 8),
                    True,
                )
                .circle()
            )
            icon_atk = (
                BuildImage.new("RGBA", (64, 64), atk_color)
                .paste(
                    BuildImage.open(BytesIO(icon_atk))
                    .convert("RGBA")
                    .resize_height(48),
                    (8, 8),
                    True,
                )
                .circle()
            )
            icon_tr = (
                BuildImage.new("RGBA", (64, 64), "#ffffff")
                .paste(
                    img_invert_rgba(Image.open(BytesIO(icon_tr)).convert("RGBA")),
                    (-2, -2),
                    True,
                )
                .circle()
            )

            c_bg = (
                BuildImage.open(BytesIO(c_bg))
                .convert("RGBA")
                .resize_height(340)
                .filter(ImageFilter.GaussianBlur(3))
            )
            c_fg = (
                BuildImage.open(BytesIO(c_fg))
                .convert("RGBA")
                .resize_height(c_bg.height)
            )
            c_bg = (
                c_bg.paste(
                    c_fg,
                    (int((c_bg.width - c_fg.width) / 2), 0),
                    True,
                )
                .paste(
                    BuildImage.new("RGBA", (c_bg.width, 65), (255, 255, 255, 120)),
                    (0, c_bg.height - 65),
                    True,
                )
                .paste(icon_atk, (10, 10), True)
                .paste(icon_def, (10, 79), True)
                .paste(icon_tr, (10, 147), True)
                .convert("RGB")
                .circle_corner(25)
                .draw_text(
                    (0, c_bg.height - 65, c_bg.width, c_bg.height),
                    (
                        localization["TimeAttackStage"][c_ri["DungeonType"]]
                        if time_atk
                        else (c_ri["Name"])
                    ),
                    max_fontsize=50,
                )
            )
            return pic.paste(c_bg, (int((pic.width - c_bg.width) / 2), 250), True)
        return None

    async def draw_birth():
        pic = pic_bg.copy().draw_text(
            (25, 25, 1375, 150),
            "学生生日",
            weight="bold",
            max_fontsize=80,
        )
        now_t = time.mktime(now.date().timetuple())
        now_w = now.weekday()
        this_week_t = now_t - now_w * 86400
        next_week_t = now_t + (7 - now_w) * 86400
        next_next_week_t = next_week_t + 7 * 86400

        birth_this_week = []
        birth_next_week = []
        for s in [x for x in students.values() if x["IsReleased"][server]]:
            birth = time.mktime(
                time.strptime(f'{now.year}/{s["BirthDay"]}', "%Y/%m/%d"),
            )
            if this_week_t <= birth < next_week_t:
                birth_this_week.append(s)
            elif next_week_t <= birth <= next_next_week_t:
                birth_next_week.append(s)

        sort_key = lambda x: x["BirthDay"].split("/")  # noqa: E731
        p_h = 0
        if birth_this_week:
            birth_this_week.sort(key=sort_key)
            p_h += 180

        if birth_next_week:
            birth_next_week.sort(key=sort_key)
            p_h += 180
            if birth_this_week:
                p_h += 10

        if p_h:
            stu_pics = [
                BuildImage.open(BytesIO(x)).convert("RGBA").resize_height(180).circle()
                for x in await asyncio.gather(
                    *[
                        schale_get(
                            f'images/student/icon/{x["CollectionTexture"]}.png',
                            True,
                        )
                        for x in birth_this_week + birth_next_week
                    ],
                )
            ]
            y_index = int((415 - p_h) / 2) + 125
            if birth_this_week:
                x_index = (
                    int((1400 - (len(birth_this_week) * (180 + 10) - 10)) / 2) + 75
                )
                pic = pic.draw_text(
                    (x_index - 165, y_index, x_index, y_index + 180),
                    "本周",
                    max_fontsize=50,
                )
                for s in birth_this_week:
                    pic.paste(stu_pics.pop(0), (x_index, y_index), True).draw_text(
                        (x_index, y_index + 180, x_index + 180, y_index + 220),
                        s["BirthDay"],
                    )
                    x_index += 180 + 10

            if birth_next_week:
                if birth_this_week:
                    y_index += 220 + 10
                x_index = (
                    int((1400 - (len(birth_next_week) * (180 + 10) - 10)) / 2) + 75
                )
                pic = pic.draw_text(
                    (x_index - 165, y_index, x_index, y_index + 180),
                    "下周",
                    max_fontsize=50,
                )
                for s in birth_next_week:
                    pic.paste(stu_pics.pop(0), (x_index, y_index), True).draw_text(
                        (x_index, y_index + 180, x_index + 180, y_index + 220),
                        s["BirthDay"],
                    )
                    x_index += 180 + 10

            return pic
        return None

    img = await asyncio.gather(  # type: ignore
        draw_gacha(),
        draw_event(),
        draw_raid(),
        draw_birth(),
    )
    img: List[BuildImage] = [x for x in img if x]
    if not img:
        img.append(
            pic_bg.copy().draw_text((0, 0, 1400, 640), "没有获取到任何数据", max_fontsize=60),
        )

    bg_w = 1500
    bg_h = 200 + sum([x.height + 50 for x in img])
    bg = (
        BuildImage.new("RGBA", (bg_w, bg_h))
        .paste(RES_CALENDER_BANNER.copy().resize((1500, 150)))
        .draw_text(
            (50, 0, 1480, 150),
            f"SchaleDB丨活动日程丨{localization['ServerName'][str(server)]}",
            max_fontsize=100,
            weight="bold",
            fill="#ffffff",
            halign="left",
        )
        .paste(
            RES_GRADIENT_BG.copy().resize(
                (1500, bg_h - 150),
                resample=Resampling.NEAREST,
            ),
            (0, 150),
        )
    )

    h_index = 200
    for im in img:
        bg.paste(im.circle_corner(10), (50, h_index), True)
        h_index += im.height + 50
    return bg.convert("RGB").save("png")


async def draw_fav_li(lvl):
    try:
        stu_li = [
            x
            for x in await schale_get_stu_data()
            if (x["MemoryLobby"] and x["MemoryLobby"][0] == lvl)
        ]
    except:
        logger.exception("获取schale db学生数据失败")
        return "获取SchaleDB学生数据失败，请检查后台输出"

    if not stu_li:
        return f"没有学生在羁绊等级{lvl}时解锁L2D"

    txt_h = 48
    pic_h = 144
    icon_w = 182
    icon_h = pic_h + txt_h
    line_max_icon = 6

    if (li_len := len(stu_li)) <= line_max_icon:
        line = 1
        length = li_len
    else:
        line = math.ceil(li_len / line_max_icon)
        length = line_max_icon

    img = RES_GRADIENT_BG.copy().resize(
        (icon_w * length, icon_h * line + 5),
        resample=Resampling.NEAREST,
    )

    async def draw_stu(name_, dev_name_, line_, index_):
        left = index_ * icon_w
        top = line_ * icon_h + 5

        ret = await schale_get(
            f"images/student/lobby/Lobbyillust_Icon_{dev_name_}_01.png",
            True,
        )
        icon_img = Image.open(BytesIO(ret)).convert("RGBA")
        img.paste(icon_img, (left, top), True)
        img.draw_text(
            (left, top + pic_h, left + icon_w, top + icon_h),
            name_,
            max_fontsize=25,
            min_fontsize=1,
        )

    task_li = []
    line = 0
    i = 0
    for stu in stu_li:
        if i == line_max_icon:
            i = 0
            line += 1
        task_li.append(draw_stu(stu["Name"], stu["DevName"], line, i))
        i += 1
    await asyncio.gather(*task_li)

    return MessageSegment.text(f"羁绊等级 {lvl} 时解锁L2D的学生有以下这些：") + MessageSegment.image(
        img.save("png"),
    )
