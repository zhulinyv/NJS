
from PIL import Image, ImageDraw, ImageFont
import os
from .api import get_ship_data_by_id
import asyncio


from .name import *
# 这个数组存放的是每张卡的中心点位置
GACHA_OFFSET = [(389, 366), (649, 366), (909, 366), (1169, 366), (1429, 366),
                (489, 713), (749, 713), (1009, 713), (1269, 713), (1529, 713)]
# 这个字典存放的是每种稀有度卡面的大小
GACHA_SIZE = {
    'Normal': (218, 310),
    'Rare': (218, 310),
    'Elite': (218, 310),
    'Super Rare': (218, 310),
    'Ultra Rare': (230, 320),
}


'''
class: Datatext
定义了向图像写入字体的时候，字体的一些属性。
'''
class Datatext:
    # L=X轴，T=Y轴，size=字体大小，fontpath=字体文件，
    def __init__(self, L, T, size, text, path, anchor = 'lt'):
        self.L = L
        self.T = T
        self.text = str(text)
        self.path = path
        self.font = ImageFont.truetype(self.path, size)
        self.anchor = anchor


def WriteText(image, font, text='text', pos=(0, 0), color=(255, 255, 255, 255), anchor='lt'):
    # 这个函数向图片上写入字符，不提供给外部调用
    rgba_image = image.convert('RGBA')
    text_overlay = Image.new('RGBA', rgba_image.size, (255, 255, 255, 0))       # 创建一张空白的透明图像，大小和之前的图像一致，否则无法合成
    image_draw = ImageDraw.Draw(text_overlay)                                   # 创建绘制对象
    image_draw.text(pos, text, font=font, fill=color, anchor=anchor)            # 绘制文字
    return Image.alpha_composite(rgba_image, text_overlay)                      # 将绘制之后的透明图像和之前的图像合成


'''
function: DrawText
args:
    image: PIL.Image 待操作的图片对象
    class_text: Datatext Datatext类
    color: tuple or str 文字的颜色（RGBA表示）
returns：
    一个PIL.Image对象，表示写入完成的图片
'''
def DrawText(image, class_text: Datatext, color=(255, 255, 255, 255)):
    font = class_text.font
    text = class_text.text
    anchor = class_text.anchor
    return WriteText(image, font, text, (class_text.L, class_text.T), color, anchor)


'''
function: DrawFillet
args:
    img: PIL.Image 待操作的图片对象
    ardii: int 表示圆角弧的半径（像素）
returns：
    一个PIL.Image对象，表示绘画完成的图片
'''
def DrawFillet(image, radii):
    # 画圆（用于分离4个角）
    circle = Image.new('L', (radii * 2, radii * 2), 0)      # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)    # 画白色圆形
    # 原图
    image = image.convert("RGBA")
    w, h = image.size
    # 画4个角（将整圆分离为4个部分）
    alpha = Image.new('L', image.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))                                  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))                  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))                  # 左下角
    # 白色区域透明可见，黑色区域不可见
    image.putalpha(alpha)
    return image


'''
function: DrawImage
args:
    base_image: PIL.Image 底图
    upper_image: PIL.Image 待粘贴的图片
    position: tuple 表示粘贴的起始位置
    opacity: int 表示透明度，1表示完全不透明，0表示完全透明，默认值是1
returns：
    一个PIL.Image对象，表示绘画完成的图片
'''
def DrawImage(base_image, upper_image, position: tuple, opacity=1.0):
    base_image.convert('RGBA')
    upper_image.convert('RGBA')

    im = AddTransparency(upper_image, opacity)
    r, g, b, a = im.split()
    return base_image.paste(im, position, mask=a)


def AddTransparency(img, factor):
    # 这个方法修改图片的透明度，不提供给外部调用
    img = img.convert('RGBA')
    img_blender = Image.new('RGBA', img.size, (0, 0, 0, 0))
    img = Image.blend(img_blender, img, factor)
    return img


'''
function: Resize
args:
    img: PIL.Image 待处理图像
    size: tuple 表示图像的新大小
returns：
    一个PIL.Image对象，表示转换完成的图片
'''
def Resize(img, size:tuple):
    img = img.resize(size, Image.ANTIALIAS)
    return img

'''
ships = [
    {
        'id': 'Collab022',          # id
        'isnew': False              # 目前只用到了id字段，其他字段没有在程序中使用，作为保留，方便日后扩展
    },
    {
        'id': 'xxx',
        'isnew': True
    },
    ...
]
'''
class GachaImage:

    def __init__(self, ships: list):
        for item in ships:
            if 'id' not in item.keys():
                raise ValueError('传入的每一项中至少应该包含“id”字段，表示抽到的船的id')
        self.ships = ships              # 保存传入的舰船id
        self.ship_num = len(ships)
        if self.ship_num > 10:
            raise ValueError('传入的船只数量不应该超过10，请检查')

    async def GetInfoByID(self):
        for i in range(len(self.ships)):
            data = await get_ship_data_by_id(self.ships[i]['id'])
            self.ships[i].update(
                {
                    'type': data['hullType'],
                    'name': data['names']['cn'],
                    'rarity': data['rarity']
                }
            )
            if data['rarity'] == 'Priority':        # 最高方案，等同于金皮
                self.ships[i]['rarity'] = 'Super Rare'
            elif data['rarity'] == 'Decisive':      # 决战方案，等同于彩皮
                self.ships[i]['rarity'] = 'Ultra Rare'
        pass

    # 这个方法完成单个卡片的绘制，返回绘制完成的Image对象
    async def MakeSinglePic(self, info):
        # print(info)
        im = Image.new('RGBA', (GACHA_SIZE[info['rarity']][0], GACHA_SIZE[info['rarity']][1] + 5), (0, 0, 0, 0))            # 透明底板
        # w, h = GACHA_SIZE[info['rarity']]
        # 绘制背景
        im_bg = Image.open(PATH_BG_GACHA.joinpath(info['rarity'] + '.png'))
        im_bg.convert('RGBA')
        DrawImage(im, im_bg, (int((im.size[0] - im_bg.size[0]) / 2), int((im.size[1] - im_bg.size[1]) / 2)))
        # 绘制角色
        try:
            im_ch = Image.open(PATH_BG_GACHA.joinpath(info['id'] + '.png'))
        except:
            im_ch = Image.open(PATH_BG_GACHA.joinpath('unknown.png'))
        im_ch.convert('RGBA')
        w, h = im.size
        if info['rarity'] == 'Ultra Rare':
            w = w - 9
            h = h - 9
        im_ch = Resize(im_ch, (int(w * 0.98), int(h * 0.98)))
        DrawImage(im, im_ch, (int((im.size[0] - im_ch.size[0]) / 2), int((im.size[1] - im_ch.size[1]) / 2)))
        # 绘制两个黑条
        im_bl = Image.new('RGBA', (218, 35), '#000000')
        DrawImage(im, im_bl, (int((im.size[0] - im_bl.size[0]) / 2), int(im.size[1] / 2) - 148), 0.4)
        DrawImage(im, im_bl, (int((im.size[0] - im_bl.size[0]) / 2), int(im.size[1] / 2) + 91), 0.4)
        # 绘制类型
        im_tp = Image.open(PATH_TYPE_GACHA.joinpath(info['type'] + '.png'))
        im_tp.convert('RGBA')
        im_tp = Resize(im_tp, (50, 30))
        DrawImage(im, im_tp, (int(im.size[0] / 2) - 107, int(im.size[1] / 2) - 144), 0.95)
        # 绘制等级
        text = Datatext(int(im.size[0] / 2) + 45, int(im.size[1] / 2) - 150, 36, 'Lv.1', FONT_GACHA_LV)
        im = DrawText(im, text, '#FFFFFF')
        # 绘制名字
        font = ImageFont.truetype(FONT_GACHA_NM, 27)
        width = font.getsize(info['name'])                      # 计算宽度
        text = Datatext(int((im.size[0] - width[0]) / 2), int(im.size[1] / 2) + 96, 27, info['name'], FONT_GACHA_NM)        # 居中画
        im = DrawText(im, text, '#FFFFFF')
        # 绘制边框
        im_ed = Image.open(PATH_EDGE_GACHA.joinpath(info['rarity'] + '.png'))
        w, h = im.size
        if info['rarity'] == 'Ultra Rare':
            w = int(w * 0.99)
            h = int(h * 0.99)
        im_ed = Resize(im_ed, (w, h))
        DrawImage(im, im_ed, (int((im.size[0] - im_ed.size[0]) / 2), int((im.size[1] - im_ed.size[1]) / 2)))
        # 绘制星星
        im_st = Image.open(PATH_STAR_GACHA.joinpath(info['rarity'] + '.png'))
        im_st = Resize(im_st, (int(im_st.size[0] * 1.5), int(im_st.size[1] * 1.5)))
        DrawImage(im, im_st, (int((im.size[0] - im_st.size[0]) / 2), int(im.size[1] / 2) + 124))

        # im.show()
        return im
        pass

    # 这个方法完成整体图像的绘制，返回CQ码
    async def Make(self):
        await self.GetInfoByID()
        im = Image.open(PATH_ROOT_GACHA.joinpath('background.jpg'))
        for i in range(self.ship_num):
            im_si = await self.MakeSinglePic(self.ships[i])
            DrawImage(im, im_si, (GACHA_OFFSET[i][0] - int(im_si.size[0] / 2), GACHA_OFFSET[i][1] - int(im_si.size[1] / 2)))
        # im.show()

        savepath = PATH.joinpath('images', 'gacha.jpg')
        im.save(savepath, 'JPEG')
        return f'[CQ:image,file=file:///{savepath}]'
        pass
    pass


if __name__ == '__main__':

    data = ['Plan001','Plan002','Plan003']

    data = [
        {
            'id': 'Plan001'
        },
        {
            'id': 'Plan002'
        },
        {
            'id': 'Plan003'
        },
        {
            'id': 'Plan004'
        },
        {
            'id': 'Plan005'
        },
        {
            'id': 'Plan006'
        },
        {
            'id': 'Plan007'
        },
        {
            'id': 'Plan008'
        },
        {
            'id': 'Plan009'
        },
        {
            'id': 'Plan010'
        }
    ]
    img = GachaImage([{'id': '258'}, {'id': '173'}, {'id': '182'}, {'id': '239'}, {'id': '295'}, {'id': '107'}, {'id': '274'}, {'id': '293'}, {'id': '166'}, {'id': '236'}])

    loop = asyncio.get_event_loop()
    task = loop.create_task(img.Make())
    loop.run_until_complete(task)
    loop.close()
    print(task.result())
