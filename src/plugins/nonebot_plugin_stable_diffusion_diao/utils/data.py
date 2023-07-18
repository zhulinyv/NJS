from ..config import config
# 基础优化tag
basetag = "masterpiece, best quality," + config.novelai_tags

# 基础排除tag
lowQuality = "easynegative,badhandv4" + config.novelai_ntags

# 屏蔽词
# htags = "nsfw|nude|naked|nipple|blood|censored|vagina|gag|gokkun|hairjob|tentacle|oral|fellatio|areolae|lactation|paizuri|piercing|sex|footjob|masturbation|hips|penis|testicles|ejaculation|cum|tamakeri|pussy|pubic|clitoris|mons|cameltoe|grinding|crotch|cervix|cunnilingus|insertion|penetration|fisting|fingering|peeing|ass|buttjob|spanked|anus|anal|anilingus|enema|x-ray|wakamezake|humiliation|tally|futa|incest|twincest|pegging|femdom|ganguro|bestiality|gangbang|3P|tribadism|molestation|voyeurism|exhibitionism|rape|spitroast|cock|69|doggystyle|missionary|virgin|shibari|bondage|bdsm|rope|pillory|stocks|bound|hogtie|frogtie|suspension|anal|dildo|vibrator|hitachi|nyotaimori|vore|amputee|transformation|bloody"
htags = r"\b(nsfw|no\s*clothes|mucus|micturition|urethra|Urinary|Urination|climax|n\s*o\s*c\s*l\s*o\s*t\s*h\s*e\s*s|n[ -]?o[ -]?c[ -]?l[ -]?o[ -]?t[ -]?h[ -]?e[ -]?s|nudity|nude|naked|nipple|blood|censored|vagina|gag|gokkun|hairjob|tentacle|oral|fellatio|areolae|lactation|paizuri|piercing|sex|footjob|masturbation|hips|penis|testicles|ejaculation|cum|tamakeri|pussy|pubic|clitoris|mons|cameltoe|grinding|crotch|cervix|cunnilingus|insertion|penetration|fisting|fingering|peeing|buttjob|spanked|anus|anal|anilingus|enema|x-ray|wakamezake|humiliation|tally|futa|incest|twincest|pegging|porn|Orgasm|womb|femdom|ganguro|bestiality|gangbang|3P|tribadism|molestation|voyeurism|exhibitionism|rape|spitroast|cock|69|doggystyle|missionary|virgin|shibari|bondage|bdsm|rope|pillory|stocks|bound|hogtie|frogtie|suspension|anal|dildo|vibrator|hitachi|nyotaimori|vore|amputee|transformation|bloody|pornhub)\b"

shapemap = {
    "square": [640, 640],
    "s": [640, 640],
    "方": [640, 640],
    "portrait": [512, 768],
    "p": [512, 768],
    "高": [512, 768],
    "landscape": [768, 512],
    "l": [768, 512],
    "宽": [768, 512],
    "uw": [900, 450],
    "uwp": [450, 900] 
}
