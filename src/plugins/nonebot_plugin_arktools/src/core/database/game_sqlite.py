"""换用tortoise-orm了"""
from tortoise.models import Model
from tortoise import fields


class BuildingBuffModel(Model):
    """后勤技能"""
    buffId = fields.CharField(null=True, max_length=255)
    buffName = fields.CharField(null=True, max_length=255)
    buffIcon = fields.CharField(null=True, max_length=255)
    skillIcon = fields.CharField(null=True, max_length=255)
    sortId = fields.IntField(null=True)
    buffColor = fields.CharField(null=True, max_length=255)
    textColor = fields.CharField(null=True, max_length=255)
    buffCategory = fields.CharField(null=True, max_length=255)
    roomType = fields.CharField(null=True, max_length=255)
    description = fields.CharField(null=True, max_length=1024)

    class Meta:
        table = "building_buff"


class CharacterModel(Model):
    """干员"""
    charId = fields.CharField(null=True, max_length=255, description="干员代码")
    name = fields.CharField(null=True, max_length=255, description="干员中文名")
    description = fields.CharField(null=True, max_length=1024)
    canUseGeneralPotentialItem = fields.BooleanField(null=True)
    canUseActivityPotentialItem = fields.BooleanField(null=True)
    potentialItemId = fields.CharField(null=True, max_length=255)
    activityPotentialItemId = fields.CharField(null=True, max_length=255)
    classicPotentialItemId = fields.CharField(null=True, max_length=255)
    nationId = fields.CharField(null=True, max_length=255)
    groupId = fields.CharField(null=True, max_length=255)
    teamId = fields.CharField(null=True, max_length=255)
    displayNumber = fields.CharField(null=True, max_length=255)
    tokenKey = fields.CharField(null=True, max_length=255)
    appellation = fields.CharField(null=True, max_length=255, description="干员外文名")
    position = fields.CharField(null=True, max_length=255, description="高台/地面")
    tagList = fields.JSONField(null=True)
    itemUsage = fields.CharField(null=True, max_length=255)
    itemDesc = fields.CharField(null=True, max_length=1024)
    itemObtainApproach = fields.CharField(null=True, max_length=255)
    isNotObtainable = fields.BooleanField(null=True)
    isSpChar = fields.BooleanField(null=True)
    maxPotentialLevel = fields.IntField(null=True)
    rarity = fields.IntField(null=True)
    profession = fields.CharField(null=True, max_length=255)
    subProfessionId = fields.CharField(null=True, max_length=255)
    trait = fields.JSONField(null=True)
    phases = fields.JSONField(null=True)
    skills = fields.JSONField(null=True)
    talents = fields.JSONField(null=True)
    potentialRanks = fields.JSONField(null=True)
    favorKeyFrames = fields.JSONField(null=True)
    allSkillLvlup = fields.JSONField(null=True)

    class Meta:
        table = "character"


class ConstanceModel(Model):
    """游戏常量"""
    maxLevel = fields.JSONField(null=True)
    characterExpMap = fields.JSONField(null=True)
    characterUpgradeCostMap = fields.JSONField(null=True)
    evolveGoldCost = fields.JSONField(null=True)
    attackMax = fields.FloatField(null=True)
    defMax = fields.FloatField(null=True)
    hpMax = fields.FloatField(null=True)
    reMax = fields.FloatField(null=True)

    class Meta:
        table = "constance"


class EquipModel(Model):
    """模组"""
    uniEquipId = fields.CharField(null=True, max_length=255)
    uniEquipName = fields.CharField(null=True, max_length=255)
    uniEquipIcon = fields.CharField(null=True, max_length=255)
    uniEquipDesc = fields.CharField(null=True, max_length=2048)
    typeIcon = fields.CharField(null=True, max_length=255)
    typeName1 = fields.CharField(null=True, max_length=255)
    typeName2 = fields.CharField(null=True, max_length=255)
    equipShiningColor = fields.CharField(null=True, max_length=255)
    showEvolvePhase = fields.IntField(null=True)
    unlockEvolvePhase = fields.IntField(null=True)
    charId = fields.CharField(null=True, max_length=255)
    tmplId = fields.CharField(null=True, max_length=255)
    showLevel = fields.IntField(null=True)
    unlockLevel = fields.IntField(null=True)
    unlockFavorPoint = fields.IntField(null=True)
    missionList = fields.JSONField(null=True)
    itemCost = fields.JSONField(null=True)
    type = fields.CharField(null=True, max_length=255)
    uniEquipGetTime = fields.IntField(null=True)
    charEquipOrder = fields.IntField(null=True)

    character = fields.CharField(null=True, max_length=255)

    template = fields.CharField(null=True, max_length=255)
    desc = fields.CharField(null=True, max_length=1024)
    paramList = fields.JSONField(null=True)
    uniEquipMissionId = fields.CharField(null=True, max_length=255)
    uniEquipMissionSort = fields.IntField(null=True)
    jumpStageId = fields.CharField(null=True, max_length=255)

    class Meta:
        table = "equip"


class HandbookInfoModel(Model):
    """档案"""
    infoId = fields.CharField(null=True, max_length=255)
    charID = fields.CharField(null=True, max_length=255)
    isLimited = fields.BooleanField(null=True)
    infoName = fields.CharField(null=True, max_length=255)
    storyTextAudio = fields.JSONField(null=True, max_length=2048)
    handbookAvgList = fields.JSONField(null=True, max_length=2048)
    sex = fields.CharField(null=True, max_length=255)

    class Meta:
        table = "handbook_info"


class HandbookStageModel(Model):
    """悖论模拟"""
    charId = fields.CharField(null=True, max_length=255)
    stageId = fields.CharField(null=True, max_length=255)
    levelId = fields.CharField(null=True, max_length=255)
    zoneId = fields.CharField(null=True, max_length=255)
    code = fields.CharField(null=True, max_length=255)
    name = fields.CharField(null=True, max_length=255)
    loadingPicId = fields.CharField(null=True, max_length=255)
    description = fields.CharField(null=True, max_length=255)
    unlockParam = fields.JSONField(null=True)
    rewardItem = fields.JSONField(null=True)
    stageNameForShow = fields.CharField(null=True, max_length=255)
    zoneNameForShow = fields.CharField(null=True, max_length=255)
    picId = fields.CharField(null=True, max_length=255)
    stageGetTime = fields.BigIntField(null=True)

    class Meta:
        table = "handbook_stage"


class ItemModel(Model):
    """物品"""
    itemId = fields.CharField(null=True, max_length=255)
    name = fields.CharField(null=True, max_length=255)
    description = fields.CharField(null=True, max_length=1024)
    rarity = fields.IntField(null=True)
    iconId = fields.CharField(null=True, max_length=255)
    overrideBkg = fields.CharField(null=True, max_length=255)
    stackIconId = fields.CharField(null=True, max_length=255)
    sortId = fields.IntField(null=True)
    usage = fields.CharField(null=True, max_length=255)
    obtainApproach = fields.CharField(null=True, max_length=255)
    classifyType = fields.CharField(null=True, max_length=255)
    itemType = fields.CharField(null=True, max_length=255)
    stageDropList = fields.JSONField(null=True)
    buildingProductList = fields.JSONField(null=True)
    hideInItemGet = fields.BooleanField(null=True)

    class Meta:
        table = "item"


class RichTextStyleModel(Model):
    """文字样式"""
    text = fields.CharField(null=True, max_length=255)
    style = fields.CharField(null=True, max_length=255)

    class Meta:
        table = "rich_text_style"


class SkillModel(Model):
    """技能"""
    skillId = fields.CharField(null=True, max_length=255)
    iconId = fields.CharField(null=True, max_length=255)
    hidden = fields.BooleanField(null=True)
    levels = fields.JSONField(null=True)

    name = fields.CharField(null=True, max_length=255)
    skillType = fields.IntField(null=True)
    durationType = fields.IntField(null=True)
    prefabId = fields.CharField(null=True, max_length=255)

    class Meta:
        table = "skill"


class TermDescriptionModel(Model):
    """特殊状态"""
    termId = fields.CharField(null=True, max_length=255)
    termName = fields.CharField(null=True, max_length=255)
    description = fields.CharField(null=True, max_length=255)

    class Meta:
        table = "term_description"


class WorkshopFormulaModel(Model):
    """制造站配方"""
    sortId = fields.IntField(null=True)
    formulaId = fields.CharField(null=True, max_length=255)
    rarity = fields.IntField(null=True)
    itemId = fields.CharField(null=True, max_length=255)
    count = fields.IntField(null=True)
    goldCost = fields.IntField(null=True)
    apCost = fields.IntField(null=True)
    formulaType = fields.CharField(null=True, max_length=255)
    buffType = fields.CharField(null=True, max_length=255)
    extraOutcomeRate = fields.FloatField(null=True)
    extraOutcomeGroup = fields.JSONField(null=True)
    costs = fields.JSONField(null=True)
    requireRooms = fields.JSONField(null=True)
    requireStages = fields.JSONField(null=True)

    class Meta:
        table = "workshop_formula"


class GachaPoolModel(Model):
    """卡池"""
    gachaPoolId = fields.CharField(null=True, max_length=255)
    gachaIndex = fields.IntField(null=True)
    openTime = fields.IntField(null=True)
    endTime = fields.IntField(null=True)
    gachaPoolName = fields.CharField(null=True, max_length=255)
    gachaPoolSummary = fields.CharField(null=True, max_length=255)
    gachaPoolDetail = fields.CharField(null=True, max_length=1024)
    guarantee5Avail = fields.IntField(null=True)
    guarantee5Count = fields.IntField(null=True)
    CDPrimColor = fields.CharField(null=True, max_length=255)
    CDSecColor = fields.CharField(null=True, max_length=255)
    LMTGSID = fields.CharField(null=True, max_length=255)
    gachaRuleType = fields.CharField(null=True, max_length=255)

    storeTextColor = fields.CharField(null=True, max_length=255)

    linkageRuleId = fields.CharField(null=True, max_length=255)
    linkageParam = fields.JSONField(null=True)

    dynMeta = fields.JSONField(null=True)

    class Meta:
        table = "gacha_pool"


class SkinModel(Model):
    """皮肤"""
    skinId = fields.CharField(null=True, max_length=255, description="皮肤代码")
    charId = fields.CharField(null=True, max_length=255, description="干员代码")
    tokenSkinMap = fields.JSONField(null=True)
    illustId = fields.CharField(null=True, max_length=255)
    dynIllustId = fields.CharField(null=True, max_length=255)
    avatarId = fields.CharField(null=True, max_length=255)
    portraitId = fields.CharField(null=True, max_length=255)
    dynPortraitId = fields.CharField(null=True, max_length=255)
    dynEntranceId = fields.CharField(null=True, max_length=255)
    buildingId = fields.CharField(null=True, max_length=255)
    battleSkin = fields.JSONField(null=True)
    isBuySkin = fields.BooleanField(null=True)
    tmplId = fields.CharField(null=True, max_length=255)
    voiceId = fields.CharField(null=True, max_length=255)
    voiceType = fields.CharField(null=True, max_length=255)
    displaySkin = fields.JSONField(null=True)

    class Meta:
        table = "skin"


class StageModel(Model):
    """关卡"""
    stageType = fields.CharField(null=True, max_length=255)
    difficulty = fields.CharField(null=True, max_length=255)
    performanceStageFlag = fields.CharField(null=True, max_length=255)
    diffGroup = fields.CharField(null=True, max_length=255)
    unlockCondition = fields.JSONField(null=True)
    stageId = fields.CharField(null=True, max_length=255)
    levelId = fields.CharField(null=True, max_length=255)
    zoneId = fields.CharField(null=True, max_length=255)
    code = fields.CharField(null=True, max_length=255)
    name = fields.CharField(null=True, max_length=255)
    description = fields.CharField(null=True, max_length=255)
    hardStagedId = fields.CharField(null=True, max_length=255)
    dangerLevel = fields.CharField(null=True, max_length=255)
    dangerPoint = fields.FloatField(null=True)
    loadingPicId = fields.CharField(null=True, max_length=255)
    canPractice = fields.BooleanField(null=True)
    canBattleReplay = fields.BooleanField(null=True)
    apCost = fields.IntField(null=True)
    apFailReturn = fields.IntField(null=True)
    etItemId = fields.CharField(null=True, max_length=255)
    etCost = fields.IntField(null=True)
    etFailReturn = fields.IntField(null=True)
    etButtonStyle = fields.CharField(null=True, max_length=255)
    apProtectTimes = fields.IntField(null=True)
    diamondOnceDrop = fields.IntField(null=True)
    practiceTicketCost = fields.IntField(null=True)
    dailyStageDifficulty = fields.IntField(null=True)
    expGain = fields.IntField(null=True)
    goldGain = fields.IntField(null=True)
    loseExpGain = fields.IntField(null=True)
    loseGoldGain = fields.IntField(null=True)
    passFavor = fields.IntField(null=True)
    completeFavor = fields.IntField(null=True)
    slProgress = fields.IntField(null=True)
    displayMainItem = fields.CharField(null=True, max_length=255)
    hilightMark = fields.BooleanField(null=True)
    bossMark = fields.BooleanField(null=True)
    isPredefined = fields.BooleanField(null=True)
    isHardPredefined = fields.BooleanField(null=True)
    isSkillSelectablePredefined = fields.BooleanField(null=True)
    isStoryOnly = fields.BooleanField(null=True)
    appearanceStyle = fields.IntField(null=True)
    stageDropInfo = fields.JSONField(null=True)
    startButtonOverrideId = fields.CharField(null=True, max_length=255)
    isStagePatch = fields.BooleanField(null=True)
    mainStageId = fields.CharField(null=True, max_length=255)

    extra_can_use = fields.BooleanField(null=True)

    class Meta:
        table = "stage"


GAME_SQLITE_MODEL_MODULE_NAME = __name__


__all__ = [
    "BuildingBuffModel",
    "CharacterModel",
    "ConstanceModel",
    "EquipModel",
    "HandbookInfoModel",
    "HandbookStageModel",
    "ItemModel",
    "RichTextStyleModel",
    "SkillModel",
    "TermDescriptionModel",
    "WorkshopFormulaModel",
    "GachaPoolModel",
    "SkinModel",
    "StageModel",

    "GAME_SQLITE_MODEL_MODULE_NAME"
]
