import os
import random
import time
from pathlib import Path
from ast import literal_eval

import nonebot
from nonebot.log import logger

from .resource.setu_message import setu_sendcd

try:
    import ujson as json
except:
    logger.warning('ujson not find, import json instead')
    import json



'''{
    'group_114':{
        'cd'       : 30,     # cd时长
        'r18'      : True,   # r18开关
        'withdraw' : 100,    # 撤回延时
        'maxnum'   : 10      # 单次最高张数
    },
    'last':{
        'user_1919' : 810    # 最近一次发送setu的时间
    },
    'ban':[
        'user_1919',         # 禁用的群组或用户，跨会话生效，会覆盖白名单设置
        'group_810'
    ]
}'''


class PermissionManager:
    def __init__(self) -> None:
        # 读取全局变量
        try: 
            self.setu_perm_cfg_path  = str(Path(nonebot.get_driver().config.setu_perm_cfg_path,'setu_perm_cfg.json'))
        except:
            self.setu_perm_cfg_path  = 'data/setu4/setu_perm_cfg.json'
        try: 
            self.setu_cd             = int(nonebot.get_driver().config.setu_cd)
        except:
            self.setu_cd             = 30
        try: 
            self.setu_withdraw_time  = int(nonebot.get_driver().config.setu_withdraw_time) if int(nonebot.get_driver().config.setu_withdraw_time)<100 else 100
        except:
            self.setu_withdraw_time  = 100
        try: 
            self.setu_max_num        = int(nonebot.get_driver().config.setu_max_num)
        except:
            self.setu_max_num        = 10
        try: 
            self.setu_enable_private = bool(literal_eval(nonebot.get_driver().config.setu_enable_private))
        except:
            self.setu_enable_private = False
        try:
            self.setu_disable_wlist  = bool(literal_eval(nonebot.get_driver().config.setu_disable_wlist))
        except:
            self.setu_disable_wlist  = False
        # 规范全局变量的取值范围
        self.setu_cd            = self.setu_cd            if self.setu_cd            > 0   else 0
        self.setu_withdraw_time = self.setu_withdraw_time if self.setu_withdraw_time > 0   else 0
        self.setu_withdraw_time = self.setu_withdraw_time if self.setu_withdraw_time < 100 else 100
        self.setu_max_num       = self.setu_max_num       if self.setu_max_num       > 1   else 1
        self.setu_max_num       = self.setu_max_num       if self.setu_max_num       < 25  else 25
        # 读取perm_cfg
        self.ReadCfg()

    # --------------- 文件读写 开始 ---------------
    # 读取cfg
    def ReadCfg(self)->dict:
        try:
            # 尝试读取
            with open(self.setu_perm_cfg_path,'r',encoding='utf-8') as f:
                self.cfg = json.loads(f.read())
            return self.cfg
        except Exception as e:
            # 读取失败
            logger.warning(f'setu_perm_cfg.json 读取失败, 尝试重建\n{e}')
            self.cfg = {}
            self.WriteCfg()
            return {}
    
    # 写入cfg
    def WriteCfg(self):
        # 尝试创建路径
        os.makedirs(self.setu_perm_cfg_path[:-18],mode=0o777,exist_ok=True)
        # 写入数据
        with open(self.setu_perm_cfg_path,'w',encoding='utf-8') as f:
            f.write(json.dumps(self.cfg))
    # --------------- 文件读写 开始 ---------------
    
    # --------------- 查询系统 开始 ---------------
    # 查询上一次发送时间
    def ReadLastSend(self,sessionId):
        try:
            return self.cfg['last'][sessionId]
        except KeyError:
            return 0

    # 查询cd
    def ReadCd(self,sessionId):
        try:
            return self.cfg[sessionId]['cd']
        except KeyError:
            return self.setu_cd
    
    # 查询撤回时间
    def ReadWithdrawTime(self,sessionId):
        try:
            return self.cfg[sessionId]['withdraw']
        except KeyError:
            return self.setu_withdraw_time

    # 查询最大张数
    def ReadMaxNum(self,sessionId):
        try:
            return self.cfg[sessionId]['maxnum']
        except KeyError:
            return self.setu_max_num

    # 查询r18
    def ReadR18(self,sessionId):
        try:
            return self.cfg[sessionId]['r18']
        except KeyError:
            return False
    
    # 查询黑名单
    def ReadBanList(self,sessionId):
        try:
            return sessionId in self.cfg['ban']
        except KeyError:
            return False

    # --------------- 查询系统 结束 ---------------
    
    # --------------- 逻辑判断 开始 ---------------
    # 查询权限, 并返回修正过的参数
    def CheckPermission(self,sessionId:str,r18flag:bool,num:int,userType:str='group'):
        logger.debug(f'-==- {sessionId} -===-\
            \ndisable_wlist  : {self.setu_disable_wlist}\
            \nenable_private : {self.setu_enable_private}\
            \nuserType       : {userType}')
        """查询权限, 并返回修正过的参数

        Args:
            sessionId (str): [会话信息]
            r18flag (bool): [是否开启r18]
            num (int): [需求张数]
            su (bool, optional): [是否为管理员]. Defaults to False.

        Raises:
            PermissionError: [未在白名单]
            PermissionError: [cd时间未到]

        Returns:
            [bool, int, int]: [r18是否启用, 图片张数, 撤回时间]
        """
        # 优先采用黑名单检查
        if self.ReadBanList(sessionId):
            logger.warning(f'涩图功能对 {sessionId} 禁用！')
            raise PermissionError(f'涩图功能对 {sessionId} 禁用！')
        # 采用白名单检查
        # 如果白名单被禁用则跳过
        if not self.setu_disable_wlist: 
            # 如果没被禁用则开始检查
            if userType == 'group' or (
               (not self.setu_enable_private) and userType == 'private'
            ):
                # 如果会话本身未在名单中, 不启用功能        
                if not sessionId in self.cfg.keys():
                    logger.warning(f'涩图功能在 {sessionId} 会话中未启用')
                    raise PermissionError('涩图功能在此会话中未启用！')
        
        
        # 查询冷却时间
        timeLeft = self.ReadCd(sessionId) + self.ReadLastSend(sessionId) - time.time()
        if timeLeft > 0:
            hours, minutes, seconds = 0, 0, 0
            if timeLeft >= 60:
                minutes, seconds = divmod(timeLeft, 60)
                hours, minutes = divmod(minutes, 60)
            else:
                seconds = timeLeft
            cd_msg = f"{str(round(hours)) + '小时' if hours else ''}{str(round(minutes)) + '分钟' if minutes else ''}{str(round(seconds,3)) + '秒' if seconds else ''}"
            logger.warning(f'setu的cd还有{cd_msg}')
            raise PermissionError(f"{random.choice(setu_sendcd)} 你的CD还有{cd_msg}！")
        
        # 检查r18权限, 图片张数, 撤回时间
        r18  = True if r18flag and self.ReadR18(sessionId) else False
        num_ = num  if num  <=  self.ReadMaxNum(sessionId) else self.ReadMaxNum(sessionId)
        return r18, num_, self.ReadWithdrawTime(sessionId)
    # --------------- 逻辑判断 结束 ---------------

    # --------------- 冷却更新 开始 ---------------
    # 最后一次发送的记录
    def UpdateLastSend(self,sessionId):
        try:
            self.cfg['last'][sessionId] = time.time()
        except KeyError:
            self.cfg['last'] = {
                sessionId : time.time()
            }
    
    # --------------- 冷却更新 结束 ---------------

    # --------------- 增删系统 开始 ---------------
    def UpdateWhiteList(self,sessionId:str,add_mode:bool):
        # 白名单部分
        if add_mode:
            if sessionId in self.cfg.keys():
                return f'{sessionId}已在白名单'
            self.cfg[sessionId] = {}
            self.WriteCfg()
            return f'成功添加{sessionId}至白名单'
        # 移除出白名单
        else:
            if sessionId in self.cfg.keys():
                self.cfg.pop(sessionId)
                self.WriteCfg()
                return f'成功移除{sessionId}出白名单'
            return f'{sessionId}不在白名单'
    
    # cd部分
    def UpdateCd(self,sessionId:str,cdTime:int):
        # 检查是否已在白名单, 不在则结束
        if not sessionId in self.cfg.keys():
            return f'{sessionId}不在白名单, 请先添加至白名单后操作'
        # 检查数据是否超出范围，超出则设定至范围内
        cdTime = cdTime if cdTime > 0 else 0
        # 读取原有数据
        try:
            cdTime_old = self.cfg[sessionId]['cd']
        except KeyError:
            cdTime_old = '未设定'
        # 写入新数据
        self.cfg[sessionId]['cd'] = cdTime
        self.WriteCfg()
        # 返回信息
        return f'成功更新冷却时间 {cdTime_old} -> {cdTime}'
    
    # 撤回时间部分
    def UpdateWithdrawTime(self,sessionId:str,withdrawTime:int):
        # 检查是否已在白名单, 不在则结束
        if not sessionId in self.cfg.keys():
            return f'{sessionId}不在白名单, 请先添加至白名单后操作'
        # 检查数据是否超出范围，超出则设定至范围内
        withdrawTime = withdrawTime if withdrawTime > 0   else 0
        withdrawTime = withdrawTime if withdrawTime < 100 else 100
        # 读取原有数据
        try:
            withdrawTime_old = self.cfg[sessionId]['withdraw']
        except KeyError:
            withdrawTime_old = '未设定'
        # 写入新数据
        self.cfg[sessionId]['withdraw'] = withdrawTime
        self.WriteCfg()
        # 返回信息
        return f'成功更新撤回时间 {withdrawTime_old} -> {withdrawTime}'
    
    # 最大张数部分
    def UpdateMaxNum(self,sessionId:str,maxNum:int):
        # 检查是否已在白名单, 不在则结束
        if not sessionId in self.cfg.keys():
            return f'{sessionId}不在白名单, 请先添加至白名单后操作'
        # 检查数据是否超出范围，超出则设定至范围内
        maxNum = maxNum if maxNum > 1  else 1
        maxNum = maxNum if maxNum < 25 else 25
        # 读取原有数据
        try:
            maxNum_old = self.cfg[sessionId]['maxnum']
        except KeyError:
            maxNum_old = '未设定'
        # 写入新数据
        self.cfg[sessionId]['maxnum'] = maxNum
        self.WriteCfg()
        # 返回信息
        return f'成功更新最大张数 {maxNum_old} -> {maxNum}'
    
    # r18部分
    def UpdateR18(self,sessionId:str,r18Mode:bool):
        # 检查是否已在白名单, 不在则结束
        if not sessionId in self.cfg.keys():
            return f'{sessionId}不在白名单, 请先添加至白名单后操作'

        if r18Mode:
            if self.ReadR18(sessionId):
                return f'{sessionId}已开启r18'
            self.cfg[sessionId]['r18'] = True
            self.WriteCfg()
            return f'成功开启{sessionId}的r18权限'
        else:
            if self.ReadR18(sessionId):
                self.cfg[sessionId]['r18'] = False
                self.WriteCfg()
                return f'成功关闭{sessionId}的r18权限'
            return f'{sessionId}未开启r18'
    
    def UpdateBanList(self,sessionId:str,add_mode:bool):
        # 加入黑名单
        if add_mode:
            try:
                if sessionId in self.cfg['ban']:
                    return f'{sessionId}已在黑名单'
            except KeyError:
                self.cfg['ban'] = []
            self.cfg['ban'].append(sessionId)
            self.WriteCfg()
            return f'成功添加{sessionId}至黑名单'
        # 移出黑名单
        else:
            try:
                self.cfg['ban'].remove(sessionId)
                self.WriteCfg()
                return f'成功移除{sessionId}出黑名单'
            except ValueError:
                return f'{sessionId}不在黑名单'
    # --------------- 增删系统 结束 ---------------
