"""与tortoise-orm对接，默认数据库是已经连接好的"""
from pathlib import Path
from typing import Optional, List, Dict, Any
from PIL import Image
import re
from tortoise.contrib.sqlite.functions import Random
from nonebot import get_driver, logger

from ..configs.path_config import PathConfig
from ..core.database.game_sqlite import *
from ..utils import (
    prof_swap,
    sub_prof_swap,
    faction_swap
)
from ..exceptions import *

pcfg = PathConfig.parse_obj(get_driver().config.dict())
gameimage_path = Path(pcfg.arknights_gameimage_path).absolute()
gamedata_path = Path(pcfg.arknights_gamedata_path).absolute()


"""CHARACTER"""
class Character:
    """干员"""

    def __init__(self, id_: str = None, data: dict = None):
        self._id = id_
        self._data = data

        self._avatar = None

    async def init(self, id_: str, data: dict = None) -> "Character":
        """异步实例化"""
        self._id = id_
        self._data = data
        if not self._data:
            data = await CharacterModel.filter(charId=self._id).first()
            if not data:
                raise  # TODO
            self._data = data.__dict__
        return self

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.name}({self.id})"

    @staticmethod
    async def parse_name(name: str) -> Optional["Character"]:
        """根据名称查"""
        data = await CharacterModel.filter(name=name).exclude(itemUsage=None)
        if not data:
            raise NamedCharacterNotExistException(details=name)
        return await Character().init(id_=data[0].charId, data=data[0].__dict__) if data else None

    @staticmethod
    async def random(
            useful: bool = True,
            prof: str = None,
            sub_prof: str = None,
            rarity: int = None,
            position: str = None
    ) -> "Character":
        """
        随机返回干员
        :param useful: 岛上的干员，而不是箱子、道具、临时招募之类的
        :param prof: 特定职业，(中文名, eg: 术师干员)
        :param sub_prof: 特定子职业，(中文名, eg: 中坚术师)
        :param rarity: 特定星数，0~5
        :param position: 特定站位，(近战 / 非近战)
        :return:
        """
        flags_ex = {}
        flags = {}
        if useful:
            flags_ex["itemObtainApproach"] = None
        if prof is not None:
            flags["profession"] = await prof_swap(prof)
        if sub_prof is not None:
            flags["subProfessionId"] = await sub_prof_swap(sub_prof)
        if rarity is not None:
            flags["rarity"] = rarity
        if position is not None:
            flags["position"] = "MELEE" if position in {"近战位", "近战"} else "RANGED"
        data = await CharacterModel.exclude(**flags_ex).filter(**flags).annotate(order=Random()).order_by("order")
        return await Character().init(id_=data[0].charId, data=data[0].__dict__) if data else None

    @staticmethod
    async def all(
            useful: bool = True,
            prof: str = None,
            sub_prof: str = None,
            rarity: int = None,
            position: str = None
    ) -> List["Character"]:
        """
        返回所有干员
        :param useful: 岛上的干员，而不是箱子、道具、临时招募之类的
        :param prof: 特定职业，(中文名, eg: 术师干员)
        :param sub_prof: 特定子职业，(中文名, eg: 中坚术师)
        :param rarity: 特定星数，0~5
        :param position: 特定站位，(近战 / 非近战)
        :return:
        """
        flags_ex = {}
        flags = {}
        if useful:
            flags_ex["itemObtainApproach"] = None
            flags_ex["charId"] = "char_1001_amiya2"
        if prof is not None:
            flags["profession"] = await prof_swap(prof)
        if sub_prof is not None:
            flags["subProfessionId"] = await sub_prof_swap(sub_prof)
        if rarity is not None:
            flags["rarity"] = rarity
        if position is not None:
            flags["position"] = "MELEE" if position in {"近战位", "近战"} else "RANGED"
        data = await CharacterModel.exclude(**flags_ex).filter(**flags).all()
        if not data:
            return []

        result = []
        for d in data:
            cht = await Character().init(id_=d.charId, data=d.__dict__)
            result.append(cht)
        return result

        # return [
        #     await Character().init(id_=d.charId, data=d.__dict__)
        #     for d in data
        # ] if data else []

    @property
    def id(self) -> str:
        """代码名(键值)"""
        return self._data["charId"]

    @property
    def name(self) -> str:
        """中文名"""
        return self._data["name"]

    @property
    def description(self) -> str:
        """简介/特性"""
        return (self._data["description"] or "").replace("\\n", "")

    @property
    def description_raw(self) -> str:
        """特性原文，有<>之类的特殊字符"""
        return self.description

    @property
    def _description_blackboard(self):
        """替换具体数值"""
        desc = self.description
        raw = re.findall(r"(\{.*?})", desc)
        for b in self._data["blackboard"]:
            for r in raw:
                if b["key"] in r:
                    desc = desc.replace(r, str(b["value"]))
                    break
        return desc

    @property
    def description_plain(self) -> str:
        """特性，纯文字"""
        desc = self.description
        if "<" in desc and ">" in desc:
            desc = re.split(r"<[@$/].*?>", desc)
            desc = "".join(desc)
        if self.trait:
            desc = self.trait[0].override_description_plain or desc
        return desc

    @property
    def nation_id(self) -> str:
        """国家代码"""
        return self._data["nationId"]

    async def get_nation_name(self) -> str:
        """国家名"""
        return await faction_swap(value=self.nation_id, type_="code2name") or ""

    @property
    def group_id(self) -> str:
        """组织代码"""
        return self._data["groupId"]

    async def get_group_name(self) -> str:
        """组织名"""
        return await faction_swap(value=self.group_id, type_="code2name") or ""

    @property
    def team_id(self) -> str:
        """队伍代码"""
        return self._data["teamId"]

    async def get_team_name(self) -> str:
        """队伍名"""
        return await faction_swap(value=self.team_id, type_="code2name") or ""

    @property
    def faction_id(self) -> str:
        """猜干员专用，阵营代码"""
        f = self.nation_id
        if self.group_id:
            f = f"{f}-{self.group_id}"
        if self.team_id:
            f = f"{f}-{self.team_id}"
        return f.strip("-")

    async def get_faction_name(self) -> str:
        """猜干员专用，阵营名"""
        f = await self.get_nation_name()
        if await self.get_group_name():
            f = f"{f}-{await self.get_group_name()}"
        if await self.get_team_name():
            f = f"{f}-{await self.get_team_name()}"
        return f.strip("-")

    @property
    def appellation(self) -> str:
        """非中文名"""
        return self._data["appellation"]

    @property
    def name_en(self) -> str:
        """非中文名"""
        return self.appellation

    @property
    def position(self) -> str:
        """位置，高台近战"""
        if self._data["position"] == "MELEE" and "可以放置于远程位" in self.description:
            return "BOTH"
        return self._data["position"]

    @property
    def tag_list(self) -> List[str]:
        return self._data["tagList"]

    @property
    def item_usage(self) -> str:
        """招聘合同描述"""
        return self._data["itemUsage"]

    @property
    def item_desc(self) -> str:
        """招聘合同简介"""
        return self._data["itemDesc"]

    @property
    def item_obtain_approach(self) -> str:
        """获取方式：主线剧情、信用交易所、凭证交易所、周年奖励、招募寻访、见习任务、活动获得、限时礼包、集成战略获得"""
        return self._data["itemObtainApproach"]

    @property
    def is_not_obtainable(self) -> bool:
        """临时招募"""
        return self._data["isNotObtainable"]

    @property
    def is_sp_char(self) -> bool:
        """异格"""
        return self._data["isSpChar"]

    @property
    def max_potential_level(self) -> int:
        """只有暴行是3，其他都是5"""
        return self._data["maxPotentialLevel"]

    @property
    def rarity(self) -> int:
        """稀有度"""
        return self._data["rarity"]

    @property
    def profession_id(self) -> str:
        """职业代码"""
        return self._data["profession"]

    async def get_profession_name(self) -> str:
        """职业名"""
        return await prof_swap(value=self.profession_id, type_="code2name")

    @property
    def sub_profession_id(self) -> str:
        """子职业代码"""
        return self._data["subProfessionId"]

    async def get_sub_profession_name(self) -> str:
        """子职业名"""
        return await sub_prof_swap(value=self.sub_profession_id, type_="code2name")

    @property
    def trait(self) -> List["CharacterTrait"]:
        """面板"""
        return [
            CharacterTrait(cht=self, data=d)
            for d in self._data["trait"]["candidates"]
        ] if self._data["trait"] else []

    @property
    def phases(self) -> List["CharacterPhase"]:
        """精英化阶段们"""
        return [
            CharacterPhase(cht=self, data=ph, level=idx)
            for idx, ph in enumerate(self._data["phases"])
        ]

    async def get_skills(self) -> List["Skill"]:
        if not self._data["skills"]:
            return []

        result = []
        for s in self._data["skills"]:
            skill = await Skill().init(id_=s["skillId"], cht=self, extra_data=s)
            result.append(skill)
        return result

        # return [
        #     await Skill().init(id_=s["skillId"], cht=self, extra_data=s)
        #     for s in self._data["skills"]
        # ] if self._data["skills"] else []

    @property
    def talents(self) -> List["CharacterTalent"]:
        """天赋们"""
        return [
            CharacterTalent(cht=self, data=d)
            for d in self._data["talents"][0]["candidates"]
        ]

    @property
    def potential_ranks(self) -> List["CharacterPotentialRank"]:
        """潜能"""
        return  # TODO

    @property
    def favor_key_frames(self) -> List["CharacterFavorKeyFrame"]:
        """好感度相关"""
        return [
            CharacterFavorKeyFrame(cht=self, data=d["data"], level=d["level"])
            for d in self._data["favorKeyFrames"]
        ]

    @property
    def all_skill_level_up(self) -> List["CharacterAllSkill"]:
        """所有技能升级相关"""
        return [
            CharacterAllSkill(cht=self, data=d)
            for d in self._data["allSkillLvlup"]
        ]

    # 不在 arknights_character_table 中的：
    async def get_skins(self) -> List["Skin"]:
        """干员的所有皮肤"""
        data = await SkinModel.filter(charId=self._id)
        if not data:
            return []

        result = []
        for d in data:
            skin = await Skin().init(id_=d.__dict__["skinId"], data=d.__dict__)
            result.append(skin)
        return result

    async def get_equips(self) -> List["Equip"]:
        """干员有的模组"""
        data = await EquipModel.filter(character=self._id, uniEquipIcon__not="original")
        if not data:
            return []

        result = []
        for d in data:
            equip = await Equip().init(id_=d.__dict__["uniEquipId"], data=d.__dict__)
            result.append(equip)
        return result

        # return [
        #     await Equip().init(id_=d.__dict__["uniEquipId"], data=d.__dict__)
        #     for d in data
        # ] if data else []

    async def get_handbook_info(self) -> "HandbookInfo":
        """干员的档案"""
        data = await HandbookInfoModel.filter(charID=self.id).first()
        if not data:
            logger.warning(f"{self.name}({self.id}) => 无 HandbookInfo!")
        return await HandbookInfo().init(id_=data.infoId, data=data.__dict__)

    async def get_sex(self) -> str:
        """性别"""
        return (await self.get_handbook_info()).story_text_audio.sex

    async def get_race(self) -> str:
        """种族"""
        return (await self.get_handbook_info()).story_text_audio.race

    @property
    def avatar(self) -> Image:
        return self._avatar or Image.open(gameimage_path / "avatar" / f"{self.id}.png")

    @avatar.setter
    def avatar(self, avatar: Image):
        self._avatar = avatar

    @property
    def skin(self) -> Image:
        """立绘(优先精二)"""
        try:
            return Image.open(gameimage_path / "skin" / f"{self.id}_2b.png")
        except FileNotFoundError:
            return Image.open(gameimage_path / "skin" / f"{self.id}_1b.png")

    # 方便使用的一些判断函数
    @property
    def can_evolve_1(self) -> bool:
        """能精一"""
        return self.rarity > 1  # 三星+

    @property
    def can_evolve_2(self) -> bool:
        """能精二"""
        return self.rarity > 2  # 四星+

    @property
    def can_all_skills_lvl_up(self) -> bool:
        """技能能升级"""
        return self.rarity > 1  # 三星+

    @property
    def can_skills_lvl_up(self) -> bool:
        """技能能专精"""
        return self.rarity > 2  # 四星+

    @property
    def has_skills(self) -> bool:
        """有技能"""
        return self.rarity > 1  # 三星+

    async def has_equips(self) -> bool:
        """有模组"""
        return await self.get_equips() != []

    # 方便用的其它函数
    async def get_tags_for_open_recruitment(self) -> List[str]:
        """公招会选到的标签"""
        tags = self.tag_list
        tags.append(await prof_swap(value=self.profession_id, type_="code2name"))  # 职业
        tags.append("近战位" if self.position == "MELEE" else "远程位")  # 位置
        tags.append(f"{await self.get_sex()}性干员" if await self.get_sex() in {"男", "女"} else "")  # 性别
        if self.rarity == 0:  # 等级
            tags.append("支援机械")
        elif self.rarity == 4:
            tags.append("资深干员")
        elif self.rarity == 5:
            tags.append("高级资深干员")
        return tags

    # 猜干员小游戏用
    async def get_drawer(self) -> str:
        """获取画师"""
        skins = await self.get_skins()
        return skins[0].drawers[0] if skins else ""


class Attributes:
    """面板"""

    def __init__(self, cht: Character = None, data: Dict[str, Any] = None):
        self._data = data
        self._character = cht

    def __str__(self):
        return (
            f"{self.character}("
            f"{self.max_hp}, "
            f"{self.attack}, "
            f"{self.defence}, "
            f"{self.resistance}, "
            f"{self.cost}, "
            f"{self.block}"
            f")"
        )

    def __repr__(self):
        return self.__str__()

    @property
    def character(self) -> Character:
        """哪个干员的"""
        return self._character

    @property
    def max_hp(self) -> int:
        """生命值"""
        return self._data["maxHp"]

    @property
    def attack(self) -> int:
        """平A攻击力"""
        return self._data["atk"]

    @property
    def defence(self) -> int:
        """物防"""
        return self._data["def"]

    @property
    def resistance(self) -> float:
        """法抗"""
        return self._data["magicResistance"]

    @property
    def cost(self) -> int:
        """费用"""
        return self._data["cost"]

    @property
    def block(self) -> int:
        """阻挡数"""
        return self._data["blockCnt"]

    @property
    def move_speed(self) -> float:
        """移速？"""
        return self._data["moveSpeed"]

    @property
    def attack_speed(self) -> float:
        """攻速"""
        return self._data["attackSpeed"]

    @property
    def base_attack_time(self) -> float:
        """攻击耗时？"""
        return self._data["baseAttackTime"]

    @property
    def respawn_time(self) -> int:
        """复活CD"""
        return self._data["respawnTime"]

    @property
    def hp_recovery(self) -> float:
        """每秒回血"""
        return self._data["hpRecoveryPerSec"]

    @property
    def sp_recovery(self) -> float:
        """每秒回蓝"""
        return self._data["spRecoveryPerSec"]

    @property
    def max_deploy_count(self) -> int:
        """最大部署数？"""
        return self._data["maxDeployCount"]

    @property
    def max_deck_stack_count(self) -> int:
        """?"""
        return self._data["maxDeckStackCnt"]

    @property
    def taunt_level(self) -> int:
        """嘲讽等级"""
        return self._data["tauntLevel"]

    @property
    def mass_level(self) -> int:
        """重量等级"""
        return self._data["massLevel"]

    @property
    def base_force_level(self) -> int:
        """力量等级"""
        return self._data["baseForceLevel"]

    @property
    def stun_immune(self) -> bool:
        """晕眩抗性"""
        return self._data["stunImmune"]

    @property
    def silence_immune(self) -> bool:
        """沉默抗性"""
        return self._data["silenceImmune"]

    @property
    def sleep_immune(self) -> bool:
        """沉睡抗性"""
        return self._data["sleepImmune"]

    @property
    def frozen_immune(self) -> bool:
        """冻结抗性"""
        return self._data["frozenImmune"]

    @property
    def levitate_immune(self) -> bool:
        """浮空抗性"""
        return self._data["levitateImmune"]


class CharacterTrait:
    """特性，如领主远程降攻为80%"""

    def __init__(self, cht: Character, data):
        self._character = cht
        self._data = data

    def __str__(self):
        return f"{self.character}({self.unlock_condition.phase}-{self.unlock_condition.level}-{self.required_potential_rank})"

    def __repr__(self):
        return self.__str__()

    @property
    def character(self) -> Character:
        """哪个干员的"""
        return self._character

    @property
    def unlock_condition(self) -> "UnlockCondition":
        """解锁特性条件"""
        return UnlockCondition(data=self._data["unlockCondition"])

    @property
    def required_potential_rank(self) -> int:
        """需要潜能等级"""
        return self._data["requiredPotentialRank"]

    @property
    def blackboard(self) -> List[Dict[str, Any]]:
        """特性具体内容"""
        return self._data["blackboard"]

    @property
    def override_description(self) -> str:
        """特性对描述的修改"""
        return self._data["overrideDescripton"] or ""

    @property
    def override_description_raw(self) -> str:
        """特性对描述的修改"""
        return self.override_description

    @property
    def _override_description_blackboard(self):
        """替换具体数值"""
        desc = self.override_description
        raw = re.findall(r"(\{.*?})", desc)
        for b in self._data["blackboard"]:
            for r in raw:
                if b["key"] in r:
                    desc = desc.replace(r, str(b["value"]))
                    break
        return desc

    @property
    def override_description_plain(self) -> str:
        """可读"""
        desc = self._override_description_blackboard
        if "<" in desc and ">" in desc:
            desc = re.split(r"<[@$/].*?>", desc)
            desc = "".join(desc)
        return desc


class CharacterPhase:
    """精英化阶段"""

    def __init__(self, cht: Character = None, data: Dict[str, Any] = None, *, level: int = -1):
        self._character = cht
        self._data = data
        self._level = level  # 标记符

    def __str__(self):
        return f"{self._character}(精{self.level})"

    def __repr__(self):
        return self.__str__()

    @property
    def level(self) -> int:
        """精英几"""
        if self._level == -1:
            raise NotImplementedError("未初始化精英化阶段")
        return self._level

    async def get_character(self) -> Character:
        """对应干员"""
        return self._character or await Character().init(id_=self._data["characterPrefabKey"])

    @property
    def max_level(self) -> int:
        """这个阶段的最高等级"""
        return self._data["maxLevel"]

    async def get_attributes(self) -> Dict[int, Attributes]:
        """阶段首尾等级对应面板"""
        return {
            f["level"]: Attributes(cht=await self.get_character(), data=f["data"])
            for f in self._data["attributesKeyFrames"]
        }

    async def get_elite_cost(self) -> List["Item"]:
        """升级到这一阶段需要材料"""
        cash = [
            await Item().init(id_="4001", count=
            (await ConstanceModel.first()).__dict__["evolveGoldCost"][(await self.get_character()).rarity][
                self.level - 1])  # 龙门币
        ]
        if not self._data["evolveCost"]:
            return cash

        result = []
        for i in self._data["evolveCost"]:
            item = await Item().init(id_=i["id"], count=i["count"])
            result.append(item)
        return result + cash

        # return (
        #     [
        #         await Item().init(id_=i["id"], count=i["count"])
        #         for i in self._data["evolveCost"]
        #     ] if self._data["evolveCost"] else []
        # ) + [
        #     await Item().init(
        #         id_="4001",
        #         count=(await ConstanceModel.first()).__dict__["evolveGoldCost"][(await self.get_character()).rarity][self.level-1])  # 龙门币
        # ]


class CharacterTalent:
    """天赋"""

    def __init__(self, cht: Character, data: Dict[str, Any]):
        self._character = cht
        self._data = data

    def __str__(self):
        return f"{self.character} - {self.name}"

    @property
    def character(self) -> Character:
        """哪个干员的"""
        return self._character

    @property
    def required_potential_rank(self) -> int:
        """潜能几"""
        return self._data["requiredPotentialRank"]

    @property
    def prefab_key(self) -> str:
        """?"""
        return self._data["prefabKey"]

    @property
    def name(self) -> str:
        """中文名"""
        return self._data["name"]

    @property
    def description(self) -> str:
        """简介"""
        return self._data["description"]

    @property
    def description_raw(self) -> str:
        """原版简介"""
        return self.description

    @property
    def description_plain(self) -> str:
        """可读"""
        desc = self.description
        if "<" in desc and ">" in desc:
            desc = re.split(r"<[@$/].*?>", desc)
            desc = "".join(desc)
        return desc

    @property
    def range_id(self) -> str:
        """?"""
        return self._data["rangeId"] or ""

    @property
    def unlock_condition(self) -> "UnlockCondition":
        """解锁条件"""
        return UnlockCondition(data=self._data["unlockCondition"])


class CharacterPotentialRank:
    """潜能"""

    def __init__(self, cht: Character, data: Dict[str, Any]):
        self._character = cht
        self._data = data

    @property
    def character(self) -> Character:
        """哪个干员的"""
        return self._character

    @property
    def type(self) -> int:
        """潜能类型"""
        return self._data["type"]

    @property
    def description(self) -> str:
        """简介"""
        return self._data["description"]

    @property
    def buff(self):
        """TODO"""
        return

    @property
    def equivalent_cost(self) -> str:
        """?"""
        return self._data["equivalentCost"] or ""


class CharacterFavorKeyFrame:
    """好感度"""

    def __init__(self, cht: Character, data: Dict[str, Any], level: int = -1):
        self._character = cht
        self._data = data
        self._level = level

    @property
    def character(self) -> Character:
        """哪个干员的"""
        return self._character

    @property
    def level(self):
        """等级？"""
        return self._level

    @property
    def attributes(self) -> Attributes:
        """面板数据"""
        return Attributes(cht=self.character, data=self._data)


class CharacterAllSkill:
    """所有技能升级(0~7)"""

    def __init__(self, cht: Character, data: Dict[str, Any]):
        self._character = cht
        self._data = data

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.character}({self.get_cost})"

    @property
    def character(self) -> Character:
        """哪个干员的"""
        return self._character

    @property
    def unlock_condition(self) -> "UnlockCondition":
        """解锁条件"""
        return UnlockCondition(data=self._data["unlockCond"])

    async def get_cost(self) -> List["Item"]:
        """升级材料"""
        result = []
        for d in self._data["lvlUpCost"]:
            item = await Item().init(id_=d["id"], count=d["count"])
            result.append(item)

        return result

        # return [
        #     await Item().init(id_=d["id"], count=d["count"])
        #     for d in self._data["lvlUpCost"]
        # ]


"""HANDBOOK"""
class HandbookInfo:
    """档案"""

    def __init__(self, id_: str = None, data: Dict[str, Any] = None):
        self._id = id_
        self._data = data

    async def init(self, id_: str, data: dict = None) -> "HandbookInfo":
        """异步实例化"""
        self._id = id_
        self._data = data
        if not self._data:
            data = await HandbookInfoModel.filter(infoId=self._id).first()
            if not data:
                raise  # TODO
            self._data = data.__dict__
        return self

    def __str__(self):
        return f"{self.story_text_audio.sex}, {self.story_text_audio.race}, {self.story_text_audio.birthplace}"

    def __repr__(self):
        return self.__str__()

    @property
    def id(self) -> str:
        """干员代码名"""
        return self._id

    async def get_character(self) -> Character:
        """哪个干员的"""
        data = await CharacterModel.filter(charId=self.id).first()
        return await Character().init(id_=self.id, data=data.__dict__)

    @property
    def story_text_audio(self) -> "HandbookInfoStoryTextAudio":
        """基本档案数据"""
        return HandbookInfoStoryTextAudio(
            handbook_info=self,
            data_basic=self._data["storyTextAudio"][0]["stories"][0],
            data_physic=self._data["storyTextAudio"][1]["stories"][0]
        )


class HandbookInfoStoryTextAudio:
    """基本档案数据等"""

    def __init__(self, handbook_info: HandbookInfo, data_basic: Dict, data_physic: Dict):
        self._handbook_info = handbook_info
        self._data_basic = data_basic
        self._data_physic = data_physic

    @property
    def handbook_info(self) -> HandbookInfo:
        """哪个档案的"""
        return self._handbook_info

    async def get_symbol(self) -> str:
        """代号，即 character.name"""
        return (await self.handbook_info.get_character()).name

    @property
    def sex(self) -> str:
        """性别"""
        return re.findall(r"【[性别|设定性别]*】(.*?)\n", self._data_basic["storyText"])[0].strip()

    @property
    def combat(self) -> str:
        """战斗经验"""
        return re.findall(r"【[战斗经验|出厂时间]*】(.*?)\n", self._data_basic["storyText"])[0].strip()

    @property
    def birthplace(self) -> str:
        """出身地"""
        return re.findall(r"【[出身地|产地]*】(.*?)\n", self._data_basic["storyText"])[0].strip()

    @property
    def birthday(self) -> str:
        """生日"""
        return re.findall(r"【[生日|出厂日]*】(.*?)\n", self._data_basic["storyText"])[0].strip()

    @property
    def race(self) -> str:
        """种族"""
        return re.findall(r"【[种族|制造商]*】(.*?)\n", self._data_basic["storyText"])[0].strip()

    @property
    def height(self) -> str:
        """身高"""
        return re.findall(r"【[身高|高度]*】(.*?)\n", self._data_basic["storyText"])[0].strip()


"""SKILL"""
class Skill:
    """干员技能"""

    def __init__(self, id_: str = None, cht: Character = None, data: Dict[str, Any] = None,
                 extra_data: Dict[str, Any] = None):
        self._id = id_
        self._character = cht
        self._data = data
        self._extra_data = extra_data  # 干员的 "skills" 中的内容

    async def init(self, id_: str, cht: Character = None, data: Dict[str, Any] = None,
                   extra_data: Dict[str, Any] = None) -> "Skill":
        """异步实例化"""
        self._id = id_
        self._character = cht
        self._data = data
        self._extra_data = extra_data  # 干员的 "skills" 中的内容
        if not self._data:
            data = await SkillModel.filter(skillId=self._id).first()
            if not data:
                raise  # TODO
            self._data = data.__dict__
        return self

    def __str__(self):
        return f"{self.character} - {self.name}({self.id})" if self.character else f"{self.name}({self.id})"

    def __repr__(self):
        return self.__str__()

    @property
    def id(self) -> str:
        """代码名"""
        return self._id

    @property
    def character(self) -> Optional["Character"]:
        """哪个干员的"""
        return self._character

    @property
    def icon_id(self) -> str:
        """图标代码名"""
        return self._data["iconId"]

    @property
    def levels(self) -> List["SkillLevel"]:
        """七个等级的技能"""
        return [
            SkillLevel(skill=self, data=d, level=idx + 1)
            for idx, d in enumerate(self._data["levels"])
        ]

    @property
    def name(self) -> str:
        """中文名"""
        return self._data["name"]

    @property
    def skill_type(self) -> int:
        """技能类型: 0, 1, 2"""
        return self._data["skillType"]

    @property
    def duration_type(self) -> int:
        """持续类型: 0, 1, 2"""
        return self._data["durationType"]

    @property
    def prefab_id(self) -> str:
        """统一技能id"""
        return self._data["prefabId"]

    ### 以下仅在有干员数据的时候可用： ###
    @property
    def override_prefab_key(self) -> str:
        """？"""
        if not self._extra_data:
            raise NotImplementedError("未输入干员数据！")
        return self._extra_data["overridePrefabKey"] or ""

    @property
    def override_token_key(self) -> str:
        """？"""
        if not self._extra_data:
            raise NotImplementedError("未输入干员数据！")
        return self._extra_data["overrideTokenKey"] or ""

    @property
    def level_up_cost_condition(self) -> List["SkillLevelUpCondition"]:
        """技能专精相关"""
        if not self._extra_data:
            raise NotImplementedError("未输入干员数据！")
        return [
            SkillLevelUpCondition(skill=self, data=d)
            for d in self._extra_data["levelUpCostCond"]
        ]

    @property
    def unlock_condition(self) -> "UnlockCondition":
        """解锁(phase, level)"""
        if not self._extra_data:
            raise NotImplementedError("未输入干员数据！")
        return UnlockCondition(data=self._extra_data["unlockCond"])

    # 不在 arknights_skill_table 中的
    @property
    def icon(self) -> Image:
        """技能图标"""
        return Image.open(gameimage_path / "skill" / f"skill_icon_{self.icon_id or self.id}.png")

    def rank(self, lvl: int = 0) -> Image:
        """专精图标"""
        return Image.open(gameimage_path / "ui" / "rank" / f"m-{lvl}.png")


class SkillLevelUpCondition:
    """技能专精"""

    def __init__(self, skill: Skill, data: Dict):
        self._skill = skill
        self._data = data

    def __str__(self):
        return f"{self.skill}({self.get_cost} - {self.time}s)"

    def __repr__(self):
        return self.__str__()

    @property
    def skill(self):
        """哪个技能的"""
        return self._skill

    @property
    def time(self) -> int:
        """专精耗时（秒）"""
        return self._data["lvlUpTime"]

    @property
    def unlock_condition(self) -> "UnlockCondition":
        """解锁条件(phase, level)"""
        return UnlockCondition(data=self._data["unlockCond"])

    async def get_cost(self) -> List["Item"]:
        """专精耗材"""
        result = []
        for i in self._data["levelUpCost"]:
            item = await Item().init(id_=i["id"], count=i["count"])
            result.append(item)
        return result

        # return [
        #     await Item().init(id_=i["id"], count=i["count"])
        #     for i in self._data["levelUpCost"]
        # ]


class SkillLevel:
    """技能等级"""

    def __init__(self, skill: Skill, data: Dict, level: int):
        self._skill = skill
        self._data = data
        self._level = level

    def __str__(self):
        return f"{self.skill} - {self.name}"

    @property
    def skill(self) -> Skill:
        """哪个技能的"""
        return self._skill

    @property
    def level(self) -> int:
        """哪个等级"""
        return self._level

    @property
    def name(self) -> str:
        """技能名"""
        return self._data["name"]

    @property
    def range_id(self) -> Optional[str]:
        """？"""
        return self._data["rangeId"] or ""

    @property
    def description(self) -> str:
        """简介(可读)"""
        return (self._data["description"] or "").replace("\\n", "")

    @property
    def description_raw(self) -> str:
        """原简介，包括<>和{}"""
        return self.description

    @property
    def _description_blackboard(self):
        """替换具体数值"""
        desc = self.description
        raw = re.findall(r"(\{.*?})", desc)
        for b in self._data["blackboard"]:
            for r in raw:
                if b["key"] in r:
                    desc = desc.replace(r, str(b["value"]))
                    break
        return desc

    @property
    def description_plain(self) -> str:
        """可读"""
        desc = self._description_blackboard
        if "<" in desc and ">" in desc:
            desc = re.split(r"<[@$/].*?>", desc)
            desc = "".join(desc)
        return desc

    @property
    def skill_type(self) -> int:
        """技能类型"""
        return self._data["skillType"]

    @property
    def duration_type(self) -> int:
        """持续类型？"""
        return self._data["durationType"]

    @property
    def sp_data(self) -> "SkillLevelSpData":
        return SkillLevelSpData(data=self._data["spData"])

    @property
    def prefab_id(self) -> str:
        """无特殊字符技能代码"""
        return self._data["prefabId"]

    @property
    def duration(self) -> float:
        """持续时间？"""
        return self._data["duration"]


class SkillLevelSpData:
    """技能相关数据"""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def sp_type(self) -> int:
        """类型"""
        return self._data["spType"]

    @property
    def max_charge_time(self) -> int:
        """最大充能次数"""
        return self._data["maxChargeTime"]

    @property
    def sp_cost(self) -> int:
        """技能耗蓝"""
        return self._data["spCost"]

    @property
    def init_sp(self) -> int:
        """技能初动"""
        return self._data["initSp"]

    @property
    def increment(self) -> float:
        """应该是蓝条增加速度"""
        return self._data["increment"]


class UnlockCondition:
    """解锁条件（phase, level）"""

    def __init__(self, data: Dict):
        self._data = data

    @property
    def phase(self) -> int:
        """精英几"""
        return self._data["phase"]

    @property
    def level(self) -> int:
        """等级几"""
        return self._data["level"]

    @property
    def favor(self) -> int:
        """好感度"""
        return self._data.get("favor", 0)


"""ITEM"""
class Item:
    """物品"""

    def __init__(self, id_: str = None, data: Dict[str, Any] = None, *, count: int = 0, weight: float = 100):
        self._id = id_
        self._count = count  # 有数量需求时填
        self._weight = weight  # 制造产物用
        self._data = data

    async def init(self, id_: str, data: Dict[str, Any] = None, *, count: int = 0, weight: float = 100) -> "Item":
        """异步实例化"""
        self._id = id_
        self._count = count  # 有数量需求时填
        self._weight = weight  # 制造产物用
        self._data = data
        if not self._data:
            data = await ItemModel.filter(itemId=self._id).first()
            if not data:
                raise  # TODO
            self._data = data.__dict__
        return self

    def __str__(self):
        return (
            f"{self.name}({self.id})({self.count})"
            if self.count
            else f"{self.name}({self.id})"
        )

    def __repr__(self):
        return self.__str__()

    @classmethod
    async def parse_name(cls, name: str) -> Optional["Item"]:
        """根据中文名获取数据"""
        data = await ItemModel.filter(name=name).first()
        if not data:
            return None
        return Item(id_=data.itemId, data=data.__dict__) if data else None

    @property
    def count(self) -> int:
        return self._count

    @property
    def weight(self) -> float:
        return self._weight

    @property
    def id(self) -> str:
        """代码名"""
        return self._id

    @property
    def name(self) -> str:
        """中文名"""
        return self._data["name"]

    @property
    def description(self) -> str:
        """简介"""
        return (self._data["description"] or "").replace("\\n", "")

    @property
    def description_raw(self) -> str:
        """原简介，包括<>和{}"""
        return self.description

    @property
    def description_plain(self) -> str:
        """可读"""
        desc = self.description
        if "<" in desc and ">" in desc:
            desc = re.split(r"<[@$/].*?>", desc)
            desc = "".join(desc)
        return desc

    @property
    def rarity(self) -> int:
        """稀有度"""
        return self._data["rarity"]

    @property
    def icon_id(self) -> str:
        """图标代码名"""
        return self._data["iconId"]

    @property
    def sort_id(self) -> int:
        """排序用"""
        return self._data["sortId"]

    @property
    def usage(self) -> str:
        """用途"""
        return self._data["usage"]

    @property
    def obtain_approach(self) -> str:
        """获取方式"""
        return self._data["obtainApproach"]

    @property
    def classify_type(self) -> str:
        """分类：CONSUME, MATERIAL, NONE"""
        return self._data["classifyType"]

    @property
    def item_type(self) -> str:
        """物品分类"""
        return self._data["itemType"]

    @property
    def stage_drop_list(self) -> List["Stage"]:
        """TODO"""
        return

    async def get_building_product_list(self) -> List["WorkshopFormula"]:
        """制造所"""
        if not self._data["buildingProductList"]:
            return []

        result = []
        for _ in self._data["buildingProductList"]:
            formula = await WorkshopFormula().init(id_=_["formulaId"])
            result.append(formula)
        return result

        # return [
        #     await WorkshopFormula().init(id_=_["formulaId"])
        #     for _ in self._data["buildingProductList"]
        # ] if self._data["buildingProductList"] else []

    # 不在 arknights_item_table 中的：
    @property
    def icon(self) -> Image:
        """技能图标"""
        return Image.open(gameimage_path / "item" / f"{self.icon_id or self.id}.png")


"""WORKSHOP_FORMULA"""
class WorkshopFormula:
    """制造站配方"""

    def __init__(self, id_: str = None, data: Dict[str, Any] = None):
        self._id = id_
        self._data = data

    async def init(self, id_: str, data: Dict[str, Any] = None) -> "WorkshopFormula":
        """异步实例化"""
        self._id = id_
        self._data = data
        if not self._data:
            data = await WorkshopFormulaModel.filter(formulaId=self._id).first()
            if not data:
                raise  # TODO
            self._data = data.__dict__
        return self

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.item_id}({self.count})"

    @property
    def id(self) -> str:
        """配方id"""
        return self._id

    @property
    def item_id(self) -> str:
        """物品id"""
        return self._data["itemId"]

    async def get_item(self) -> Item:
        """物品"""
        return await Item().init(id_=self.item_id)

    @property
    def rarity(self) -> int:
        """稀有度？"""
        return self._data["rarity"]

    @property
    def count(self) -> int:
        """制造数量"""
        return self._data["count"]

    @property
    def gold_cost(self) -> int:
        """消耗多少币"""
        return self._data["goldCost"]

    @property
    def ap_cost(self) -> int:
        """消耗时间（秒）"""
        return self._data["apCost"]

    @property
    def formula_type(self) -> str:
        """配方类型"""
        return self._data["formulaType"]

    @property
    def buff_type(self) -> str:
        """?"""
        return self._data["buffType"]

    @property
    def extra_outcome_rate(self) -> float:
        """额外物品制造出的概率"""
        return self._data["extraOutcomeRate"]

    async def get_extra_outcome_group(self) -> List["Item"]:
        """额外产物及产率"""
        if not self._data["extraOutcomeGroup"]:
            return []

        result = []
        for _ in self._data["extraOutcomeGroup"]:
            item = await Item().init(id_=_["itemId"], count=_["itemCount"], weight=_["weight"])
            result.append(item)

        return result

        # return [
        #     await Item().init(id_=_["itemId"], count=_["itemCount"], weight=_["weight"])
        #     for _ in self._data["extraOutcomeGroup"]
        # ] if self._data["extraOutcomeGroup"] else []

    async def get_costs(self) -> List["Item"]:
        """消耗物品"""
        if not self._data["costs"]:
            return []

        result = []
        for _ in self._data["costs"]:
            item = await Item().init(id_=_["id"], count=_["count"])
            result.append(item)

        return result

        # return [
        #     await Item().init(id_=_["id"], count=_["count"])
        #     for _ in self._data["costs"]
        # ] if self._data["costs"] else []

    @property
    def require_rooms(self) -> List["Room"]:
        """TODO"""
        return

    @property
    def require_stages(self) -> List["Stage"]:
        """TODO"""
        return


"""EQUIP"""
class Equip:
    """模组"""

    def __init__(self, id_: str = None, data: Dict = None):
        self._id = id_
        self._data = data

    async def init(self, id_: str, data: Dict = None) -> "Equip":
        """异步实例化"""
        self._id = id_
        self._data = data
        if not self._data:
            data = await EquipModel.filter(uniEquipId=self._id).first()
            if not data:
                raise  # TODO
            self._data = data.__dict__
        return self

    def __str__(self):
        return f"{self.name}({self.id})"

    def __repr__(self):
        return self.__str__()

    async def get_character(self) -> Character:
        """哪个干员的"""
        return await Character().init(id_=self._data["charId"])

    @property
    def id(self) -> str:
        """代码名"""
        return self._id

    @property
    def name(self) -> str:
        """中文名"""
        return self._data["uniEquipName"]

    @property
    def icon_id(self) -> str:
        """图标名"""
        return self._data["uniEquipIcon"]

    @property
    def description(self) -> str:
        """模组描述"""
        return self._data["uniEquipDesc"]

    @property
    def type_icon(self) -> str:
        """类型图标名"""
        return self._data["typeIcon"]

    @property
    def type_name(self) -> str:
        """类型名"""
        return f"{self._data['typeName1']}{'-' + self._data['typeName2'] if self._data['typeName2'] != 'None' else ''}"

    @property
    def unlock_condition(self) -> "UnlockCondition":
        """解锁条件"""
        return UnlockCondition(
            data={
                "phase": self._data["unlockEvolvePhase"],
                "level": self._data["unlockLevel"],
                "favor": self._data["unlockFavorPoint"]
            }
        )

    @property
    def mission_list(self) -> List["Mission"]:
        """TODO: 解锁任务"""
        return

    async def get_item_cost(self) -> Dict[int, List["Item"]]:
        """解锁物品"""
        if not self._data["itemCost"]:
            return {}

        result = {}
        for idx, d in enumerate(self._data["itemCost"].values()):
            costs = []
            for i in d:
                item = await Item().init(id_=i["id"], count=i["count"])
                costs.append(item)
            result[idx] = costs
        return result

        # 很怪，用下方法无法通过nb发布检查：SyntaxError: asynchronous comprehension outside of an asynchronous function
        # return {
        #     idx: [
        #         await Item().init(id_=i["id"], count=i["count"])
        #         for i in d
        #     ] for idx, d in enumerate(self._data["itemCost"].values())
        # } if self._data["itemCost"] else {}

    # 不在 arknights_equip_table 中的:
    def rank(self, lvl: int = 0):
        """模组1,2,3级图标"""
        return Image.open(gameimage_path / "equip" / "stage" / f"img_stg{lvl}.png")


"""GACHA_POOL"""
class GachaPool:
    def __init__(self, id_: str = None, data: Dict = None):
        self._id = id_
        self._data = data

    async def init(self, id_: str, data: Dict = None) -> "GachaPool":
        """异步实例化"""
        self._id = id_
        self._data = data
        if not self._data:
            data = await GachaPoolModel.filter(gachaPoolId=self._id).first()
            if not data:
                raise  # TODO
            self._data = data.__dict__
        return self

    def __str__(self):
        return f"{self.name}({self.id})({self.rule_type})"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    async def parse_name(name: str) -> Optional["GachaPool"]:
        """根据名称查"""
        data = await GachaPoolModel.filter(gachaPoolName=name).first()
        if not data:
            raise NamedPoolNotExistException(details=name)
        return await GachaPool().init(id_=data.gachaPoolId, data=data.__dict__) if data else None

    @staticmethod
    async def random(
            named: bool = True,
            rule: str = None
    ) -> Optional["GachaPool"]:
        """
        随机返回池子
        :param named: 有池子专属名字
        :param rule: 池子类型：ATTAIN, NORMAL, LIMITED, LINKAGE
        :return:
        """
        flags_ex = {}
        flags = {}
        if named:
            flags_ex["gachaPoolName"] = "适合多种场合的强力干员"
        if rule:
            flags["gachaRuleType"] = rule if rule in {"ATTAIN", "NORMAL", "LIMITED", "LINKAGE"} else "NORMAL"

        data = await GachaPoolModel.exclude(**flags_ex).filter(**flags).annotate(order=Random()).order_by("order")
        if not data:
            return None
        return await GachaPool().init(id_=data[0].gachaPoolId, data=data[0].__dict__) if data else None

    @staticmethod
    async def all(
            named: bool = True,
            rule: str = None
    ) -> List["GachaPool"]:
        """
        返回所有池子
        :param named: 有池子专属名字
        :param rule: 池子类型：ATTAIN, NORMAL, LIMITED, LINKAGE
        :return:
        """
        flags_ex = {}
        flags = {}
        if named:
            flags_ex["gachaPoolName"] = "适合多种场合的强力干员"
        if rule:
            flags["gachaRuleType"] = rule if rule in {"ATTAIN", "NORMAL", "LIMITED", "LINKAGE"} else "NORMAL"
        data = await GachaPoolModel.exclude(**flags_ex).filter(**flags).all()
        if not data:
            return []

        result = []
        for d in data:
            cht = await GachaPool().init(id_=d.gachaPoolId, data=d.__dict__)
            result.append(cht)
        return result

    @property
    def id(self) -> str:
        """代码名"""
        return self._data["gachaPoolId"]

    @property
    def index(self) -> int:
        """？"""
        return self._data["gachaIndex"]

    @property
    def open_timestamp(self) -> int:
        """开池子时间戳"""
        return self._data["openTime"]

    @property
    def end_timestamp(self) -> int:
        """关池子时间戳"""
        return self._data["endTime"]

    @property
    def name(self) -> str:
        """池子名"""
        return self._data["gachaPoolName"]

    @property
    def summary(self) -> str:
        """关池子的具体时间"""
        return self._data["gachaPoolSummary"]

    @property
    def detail(self) -> str:
        """池子描述（能抽出的干员）"""
        return self._data["gachaPoolDetail"]

    @property
    def rule_type(self) -> str:
        """池子类型"""
        return self._data["gachaRuleType"]


"""SKIN"""
class Skin:
    """皮肤"""

    def __init__(self, id_: str = None, data: dict = None):
        self._id = id_
        self._data = data

    async def init(self, id_: str, data: dict = None) -> "Skin":
        """异步实例化"""
        self._id = id_
        self._data = data
        if not self._data:
            data = await SkinModel.filter(skinId=self._id).first()
            if not data:
                raise  # TODO
            self._data = data.__dict__
        return self

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.name}({self.id})"

    async def get_character(self) -> "Character":
        """哪个干员的"""
        return await Character().init(id_=self._data["charId"])

    @property
    def id(self) -> str:
        """皮肤代码"""
        return self._data["skinId"]

    @property
    def illust_id(self) -> str:
        """画师代码"""
        return self._data["illustId"]

    @property
    def avatar_id(self) -> str:
        """干员头图代码"""
        return self._data["avatarId"]

    @property
    def portrait_id(self) -> str:
        """干员半身像代码"""
        return self._data["portraitId"]

    @property
    def building_id(self) -> str:
        """?"""
        return self._data["buildingId"]

    @property
    def is_buy_skin(self) -> bool:
        """?"""
        return self._data["isBuySkin"]

    @property
    def display_skin(self) -> "SkinDisplaySkin":
        """显示信息"""
        return SkinDisplaySkin(skin=self, data=self._data["displaySkin"])

    # 不在 table 中的
    @property
    def name(self) -> str:
        """名称"""
        return self.display_skin.name or self.display_skin.group_name

    @property
    def description(self) -> str:
        """介绍"""
        return self.display_skin.description or self.display_skin.content

    @property
    def drawers(self) -> List[str]:
        """画师们"""
        return self.display_skin.drawers


class SkinDisplaySkin:
    """显示信息"""

    def __init__(self, skin: "Skin", data):
        self._skin = skin
        self._data = data

    @property
    def skin(self) -> "Skin":
        """哪个皮肤的"""
        return self._skin

    @property
    def name(self) -> str:
        """皮肤名"""
        return self._data["skinName"]

    @property
    def drawers(self) -> List[str]:
        """画师们"""
        return self._data["drawerList"]

    @property
    def group_id(self) -> str:
        """分类代码，默认为 “ILLUST_0” """
        return self._data["skinGroupId"]

    @property
    def group_name(self) -> str:
        """分类名，默认为 “默认服装” """
        return self._data["skinGroupName"]

    @property
    def content(self) -> str:
        """介绍？"""
        return self._data["content"]

    @property
    def dialog(self) -> str:
        """也是介绍？"""
        return self._data["dialog"]

    @property
    def usage(self) -> str:
        """还是介绍？"""
        return self._data["usage"]

    @property
    def description(self) -> str:
        """好多介绍"""
        return self._data["description"]

    @property
    def obtain(self) -> str:
        """获取方式"""
        return self._data["obtainApproach"]

    @property
    def time(self) -> int:
        """获取时间"""
        return self._data["getTime"]


"""TODO"""
class Stage: ...
class Room: ...
class Mission: ...


__all__ = [
    "Character",
    "Skill",
    "Item",
    "Equip",
    "GachaPool",
    "Skin"
]
