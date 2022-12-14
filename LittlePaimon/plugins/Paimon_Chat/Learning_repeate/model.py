import atexit
import random
import re
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property, cmp_to_key
from typing import Generator, List, Optional, Union, Tuple, Dict, Any

import jieba_fast.analyse
import pymongo
import pypinyin
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11 import Message

from ...utils.config import config

mongo_client = pymongo.MongoClient(config.paimon_mongodb_url)

mongo_db = mongo_client['PaimonChat']

message_mongo = mongo_db['message']
message_mongo.create_index(name='time_index',
                           keys=[('time', pymongo.DESCENDING)])

context_mongo = mongo_db['context']
context_mongo.create_index(name='keywords_index',
                           keys=[('keywords', pymongo.HASHED)])
context_mongo.create_index(name='count_index',
                           keys=[('count', pymongo.DESCENDING)])
context_mongo.create_index(name='time_index',
                           keys=[('time', pymongo.DESCENDING)])
context_mongo.create_index(name='answers_index',
                           keys=[('answers.group_id', pymongo.TEXT),
                                 ('answers.keywords', pymongo.TEXT)],
                           default_language='none')

blacklist_mongo = mongo_db['blacklist']
blacklist_mongo.create_index(name='group_index',
                             keys=[('group_id', pymongo.HASHED)])


@dataclass
class ChatData:
    group_id: int
    user_id: int
    raw_message: str
    plain_text: str
    time: int
    bot_id: int

    _keywords_size: int = 3

    @cached_property
    def is_plain_text(self) -> bool:
        return '[CQ:' not in self.raw_message and len(self.plain_text) != 0

    @cached_property
    def is_image(self) -> bool:
        return '[CQ:image,' in self.raw_message or '[CQ:face,' in self.raw_message

    @cached_property
    def keywords(self) -> str:
        if not self.is_plain_text and len(self.plain_text) == 0:
            return self.raw_message

        keywords_list = jieba_fast.analyse.extract_tags(
            self.plain_text, topK=ChatData._keywords_size)
        if len(keywords_list) < 2:
            return self.plain_text
        else:
            # keywords_list.sort()
            return ' '.join(keywords_list)

    @cached_property
    def keywords_pinyin(self) -> str:
        return ''.join([item[0] for item in pypinyin.pinyin(
            self.keywords, style=pypinyin.NORMAL, errors='default')]).lower()

    @cached_property
    def to_me(self) -> bool:
        return self.plain_text.startswith('?????????')


class Chat:
    answer_threshold = config.paimon_answer_threshold            # answer ?????????????????????????????????????????????????????????
    answer_limit_threshold = config.paimon_answer_limit_threshold     # ??????????????????????????????????????????????????? 50 ????????????????????? bot ?????????????????????
    cross_group_threshold = config.paimon_cross_group_threshold      # N ??????????????????????????????????????????????????????
    repeat_threshold = config.paimon_repeat_threshold            # ?????????????????????????????????????????????????????????????????????
    speak_threshold = config.paimon_speak_threshold             # ??????????????????????????????????????????

    drunk_probability = config.paimon_drunk_probability        # ????????????????????????????????????????????????
    split_probability = 0.5         # ?????????????????????????????????
    voice_probability = config.paimon_voice_probability           # ???????????????????????????????????????
    speak_continuously_probability = config.paimon_speak_continuously_probability  # ???????????????????????????
    speak_poke_probability = config.paimon_speak_poke_probability    # ????????????????????????????????????????????????
    speak_continuously_max_len = config.paimon_speak_continuously_max_len  # ?????????????????????????????????

    save_time_threshold = 3600      # ????????????????????????????????? ( ??? )
    save_count_threshold = 1000     # ???????????????????????????????????????????????????????????????????????????????????????

    blacklist_answer = defaultdict(set)
    blacklist_answer_reserve = defaultdict(set)

    learningGroup = config.paimon_chat_group# ??????????????????

    def __init__(self, data: Union[ChatData, GroupMessageEvent, PrivateMessageEvent]):

        if isinstance(data, ChatData):
            self.chat_data = data
        elif isinstance(data, GroupMessageEvent):
            self.chat_data = ChatData(
                group_id=data.group_id,
                user_id=data.user_id,
                # ?????????????????????????????????????????????????????????????????????????????????
                raw_message=re.sub(
                    r',subType=\d+\]',
                    r']',
                    data.raw_message),
                plain_text=data.get_plaintext(),
                time=data.time,
                bot_id=data.self_id,
            )
        elif isinstance(data, PrivateMessageEvent):
            event_dict = data.dict()
            self.chat_data = ChatData(
                group_id=data.user_id,  # ??????????????????????????????????????????
                user_id=data.user_id,
                # ?????????????????????????????????????????????????????????????????????????????????
                raw_message=re.sub(
                    r',subType=\d+\]',
                    r']',
                    data.raw_message),
                plain_text=data.get_plaintext(),
                time=data.time,
                bot_id=data.self_id,
            )

    def learn(self) -> bool:
        """
        ???????????????
        """

        if len(self.chat_data.raw_message.strip()) == 0:
            return False

        group_id = self.chat_data.group_id
        if group_id in Chat._message_dict:
            group_msgs = Chat._message_dict[group_id]
            if group_msgs:
                group_pre_msg = group_msgs[-1]
            else:
                group_pre_msg = None

            # ????????????????????????
            self._context_insert(group_pre_msg)

            user_id = self.chat_data.user_id
            if group_pre_msg and group_pre_msg['user_id'] != user_id:
                # ????????????????????????????????????????????????????????????
                for msg in group_msgs[:-3:-1]:
                    if msg['user_id'] == user_id:
                        self._context_insert(msg)
                        break

        self._message_insert()
        return True

    def answer(self, with_limit: bool = True) -> Optional[Generator[Message, None, None]]:
        """
        ???????????????????????????????????????????????????????????????
        """

        group_id = self.chat_data.group_id
        bot_id = self.chat_data.bot_id
        group_bot_replies = Chat._reply_dict[group_id][bot_id]

        if with_limit:
            # # ????????????????????????????????????????????????????????????
            # if self.chat_data.is_plain_text and len(self.chat_data.plain_text) < 2:
            #     return None

            if len(group_bot_replies):
                latest_reply = group_bot_replies[-1]
                # ??????????????????????????? 6 ?????????
                if int(time.time()) - latest_reply['time'] < 6:
                    return None
                # # ?????????????????????????????????
                # if self.chat_data.raw_message == latest_reply['pre_raw_message']:
                #     return None
                # ????????????????????????????????????????????????
                # if self.chat_data.raw_message == latest_reply['reply']:
                #    return None

        results = self._context_find()

        if results:
            raw_message = self.chat_data.raw_message
            keywords = self.chat_data.keywords
            with Chat._reply_lock:
                group_bot_replies.append({
                    'time': int(time.time()),
                    'pre_raw_message': raw_message,
                    'pre_keywords': keywords,
                    'reply': '[PaimonChat: Reply]',  # flag
                    'reply_keywords': '[PaimonChat: Reply]',  # flag
                })

            def yield_results(results: Tuple[List[str], str]) -> Generator[Message, None, None]:
                answer_list, answer_keywords = results
                group_bot_replies = Chat._reply_dict[group_id][bot_id]
                for item in answer_list:
                    with Chat._reply_lock:
                        group_bot_replies.append({
                            'time': int(time.time()),
                            'pre_raw_message': raw_message,
                            'pre_keywords': keywords,
                            'reply': item,
                            'reply_keywords': answer_keywords,
                        })
                    if '[CQ:' not in item and len(item) > 1 \
                            and random.random() < Chat.voice_probability:
                        yield Chat._text_to_speech(item)
                    else:
                        yield Message(item)

                with Chat._reply_lock:
                    group_bot_replies = group_bot_replies[-Chat._save_reserve_size:]

            return yield_results(results)

        return None

    @staticmethod
    def speak() -> Optional[Tuple[int, int, List[Message]]]:
        """
        ????????????????????????????????????????????? bot ?????????????????????????????? List????????????????????????
        """

        basic_msgs_len = 10
        basic_delay = 600

        def group_popularity_cmp(lhs: Tuple[int, List[Dict[str, Any]]],
                                 rhs: Tuple[int, List[Dict[str, Any]]]) -> int:

            def cmp(a: Any, b: Any):
                return (a > b) - (a < b)

            lhs_group_id, lhs_msgs = lhs
            rhs_group_id, rhs_msgs = rhs

            lhs_len = len(lhs_msgs)
            rhs_len = len(rhs_msgs)

            # ????????? 0, ?????? 1 ???????????????
            lhs_drunkenness = Chat._drunkenness_dict[lhs_group_id] + 1
            rhs_drunkenness = Chat._drunkenness_dict[rhs_group_id] + 1

            if lhs_len < basic_msgs_len or rhs_len < basic_msgs_len:
                return cmp(lhs_len * lhs_drunkenness,
                           rhs_len * rhs_drunkenness)

            lhs_duration = lhs_msgs[-1]['time'] - lhs_msgs[0]['time']
            rhs_duration = rhs_msgs[-1]['time'] - rhs_msgs[0]['time']

            if not lhs_duration or not rhs_duration:
                return cmp(lhs_len, rhs_len)

            return cmp(lhs_len * lhs_drunkenness / lhs_duration,
                       rhs_len * rhs_drunkenness / rhs_duration)

        # ?????????????????????
        popularity = sorted(Chat._message_dict.items(),
                            key=cmp_to_key(group_popularity_cmp))

        cur_time = time.time()
        for group_id, group_msgs in popularity:
            group_replies = Chat._reply_dict[group_id]
            if not len(group_replies) or len(group_msgs) < basic_msgs_len:
                continue

            # ????????????????????????????????????????????????????????????????????????????????????????????????????????????[0]?????????
            group_replies_front = list(group_replies.values())[0]
            if not len(group_replies_front) or \
                    group_replies_front[-1]['time'] > group_msgs[-1]['time']:
                continue

            msgs_len = len(group_msgs)
            latest_time = group_msgs[-1]['time']
            duration = latest_time - group_msgs[0]['time']
            avg_interval = duration / msgs_len

            # ?????????????????????????????? N ????????????????????????????????????????????????
            # print(cur_time - latest_time, '/', avg_interval *
            #       Chat.speak_threshold + basic_delay)
            if cur_time - latest_time < avg_interval * Chat.speak_threshold + basic_delay:
                continue

            # append ?????? flag, ???????????????????????????????????????????????????????????? context ???????????? speak ??????????????????????????????
            with Chat._reply_lock:
                group_replies_front.append({
                    'time': int(cur_time),
                    'pre_raw_message': '[PaimonChat: Speak]',
                    'pre_keywords': '[PaimonChat: Speak]',
                    'reply': '[PaimonChat: Speak]',
                    'reply_keywords': '[PaimonChat: Speak]',
                })

            available_time = cur_time - 24 * 3600
            speak_context = context_mongo.aggregate([
                {
                    '$match': {
                        'count': {
                            '$gt': Chat.answer_threshold
                        },
                        'time': {
                            '$gt': available_time
                        },
                        # ???????????????????????????????????????????????????????????????????????????
                        'answers.group_id': group_id,
                        'answers.time': {
                            '$gt': available_time
                        },
                        'answers.count': {
                            '$gt': Chat.answer_threshold
                        }
                    }
                }, {
                    '$sample': {'size': 1}  # ????????????
                }
            ])

            speak_context = list(speak_context)
            if not speak_context:
                continue

            ban_keywords = Chat._find_ban_keywords(
                context=speak_context[0], group_id=group_id)
            messages = [answer['messages']
                        for answer in speak_context[0]['answers']
                        if answer['count'] >= Chat.answer_threshold
                        and answer['keywords'] not in ban_keywords
                        and answer['group_id'] == group_id]

            if not messages:
                continue

            speak = random.choice(random.choice(messages))

            bot_id = random.choice(
                [bid for bid in group_replies.keys() if bid])
            with Chat._reply_lock:
                group_replies[bot_id].append({
                    'time': int(cur_time),
                    'pre_raw_message': '[PaimonChat: Speak]',
                    'pre_keywords': '[PaimonChat: Speak]',
                    'reply': speak,
                    'reply_keywords': '[PaimonChat: Speak]',
                })

            speak_list = [Message(speak), ]
            while random.random() < Chat.speak_continuously_probability \
                    and len(speak_list) < Chat.speak_continuously_max_len:
                pre_msg = str(speak_list[-1])
                answer = Chat(ChatData(group_id, 0, pre_msg,
                                       pre_msg, cur_time, 0)).answer(False)
                if not answer:
                    break
                speak_list.extend(answer)

            if random.random() < Chat.speak_poke_probability:
                target_id = random.choice(
                    Chat._message_dict[group_id])['user_id']
                speak_list.append(Message('[CQ:poke,qq={}]'.format(target_id)))

            return bot_id, group_id, speak_list

        return None

    @staticmethod
    def ban(group_id: int, bot_id: int, ban_raw_message: str, reason: str) -> bool:
        """
        ???????????????????????????????????????????????????
        """

        if group_id not in Chat._reply_dict:
            return False

        ban_reply = None
        reply_data = Chat._reply_dict[group_id][bot_id][::-1]

        for reply in reply_data:
            cur_reply = reply['reply']
            # ?????????????????? ban ??????????????????
            if not ban_raw_message or ban_raw_message in cur_reply:
                ban_reply = reply
                break

        # ??????????????????????????? CQ ??????????????????????????????????????????????????????????????????????????????
        if not ban_reply:
            search = re.search(r'(\[CQ:[a-zA-z0-9-_.]+)',
                               ban_raw_message)
            if search:
                type_keyword = search.group(1)
                for reply in reply_data:
                    cur_reply = reply['reply']
                    if type_keyword in cur_reply:
                        ban_reply = reply
                        break

        if not ban_reply:
            return False

        pre_keywords = reply['pre_keywords']
        keywords = reply['reply_keywords']

        # ?????????????????????????????????????????????????????????????????????????????? update
        # context_mongo.update_one({
        #     'keywords': pre_keywords,
        #     'answers.keywords': keywords,
        #     'answers.group_id': group_id
        # }, {
        #     '$set': {
        #         'answers.$.count': -99999
        #     }
        # })
        context_mongo.update_one({
            'keywords': pre_keywords
        }, {
            '$push': {
                'ban': {
                    'keywords': keywords,
                    'group_id': group_id,
                    'reason': reason,
                    'time': int(time.time())
                }
            }
        })
        if keywords in Chat.blacklist_answer_reserve[group_id]:
            Chat.blacklist_answer[group_id].add(keywords)
            if keywords in Chat.blacklist_answer_reserve[Chat._blacklist_flag]:
                Chat.blacklist_answer[Chat._blacklist_flag].add(
                    keywords)
        else:
            Chat.blacklist_answer_reserve[group_id].add(keywords)

        return True

    @staticmethod
    def drink(group_id: int) -> None:
        """
        ??????????????????????????????????????????????????????????????????????????????????????????
        """
        Chat._drunkenness_dict[group_id] += 1

    @staticmethod
    def sober_up(group_id: int) -> bool:
        """
        ???????????????????????????????????????????????????????????????
        """

        Chat._drunkenness_dict[group_id] -= 1
        return Chat._drunkenness_dict[group_id] <= 0

# private:
    _reply_dict = defaultdict(lambda: defaultdict(list))  # ????????????????????????????????????????????????
    _message_dict = {}              # ???????????????
    _drunkenness_dict = defaultdict(int)          # ?????????????????????????????????????????????

    _save_reserve_size = 100        # ???????????????????????????????????????
    _late_save_time = 0             # ???????????????????????????????????????????????? ( time.time(), ??? )

    _reply_lock = threading.Lock()
    _message_lock = threading.Lock()
    _blacklist_flag = 114514

    def _message_insert(self):
        group_id = self.chat_data.group_id

        with Chat._message_lock:
            if group_id not in Chat._message_dict:
                Chat._message_dict[group_id] = []

            Chat._message_dict[group_id].append({
                'group_id': group_id,
                'user_id': self.chat_data.user_id,
                'raw_message': self.chat_data.raw_message,
                'is_plain_text': self.chat_data.is_plain_text,
                'plain_text': self.chat_data.plain_text,
                'keywords': self.chat_data.keywords,
                'time': self.chat_data.time,
            })

        cur_time = self.chat_data.time
        if Chat._late_save_time == 0:
            Chat._late_save_time = cur_time - 1
            return

        if len(Chat._message_dict[group_id]) > Chat.save_count_threshold:
            Chat._sync(cur_time)

        elif cur_time - Chat._late_save_time > Chat.save_time_threshold:
            Chat._sync(cur_time)

    @staticmethod
    def _sync(cur_time: int = time.time()):
        """
        ?????????
        """

        with Chat._message_lock:
            save_list = [msg
                         for group_msgs in Chat._message_dict.values()
                         for msg in group_msgs
                         if msg['time'] > Chat._late_save_time]
            if not save_list:
                return

            Chat._message_dict = {group_id: group_msgs[-Chat._save_reserve_size:]
                                  for group_id, group_msgs in Chat._message_dict.items()}

            Chat._late_save_time = cur_time

        message_mongo.insert_many(save_list)

    def _context_insert(self, pre_msg):
        if not pre_msg:
            return

        raw_message = self.chat_data.raw_message

        # ??????????????????
        if pre_msg['raw_message'] == raw_message:
            return

        # ????????????????????????
        if '[CQ:reply,' in raw_message:
            return

        keywords = self.chat_data.keywords
        group_id = self.chat_data.group_id
        pre_keywords = pre_msg['keywords']
        cur_time = self.chat_data.time

        # update_key = {
        #     'keywords': pre_keywords,
        #     'answers.keywords': keywords,
        #     'answers.group_id': group_id
        # }
        # update_value = {
        #     '$set': {'time': cur_time},
        #     '$inc': {'answers.$.count': 1},
        #     '$push': {'answers.$.messages': raw_message}
        # }
        # # update_value.update(update_key)

        # context_mongo.update_one(
        #     update_key, update_value, upsert=True)

        # ?????? upsert ????????????????????????_(:????????)_
        # ?????? find + insert or update ?????????
        find_key = {'keywords': pre_keywords}
        context = context_mongo.find_one(find_key)
        if context:
            update_value = {
                '$set': {
                    'time': cur_time
                },
                '$inc': {'count': 1}
            }
            answer_index = next((idx for idx, answer in enumerate(context['answers'])
                                 if answer['group_id'] == group_id
                                 and answer['keywords'] == keywords), -1)
            if answer_index != -1:
                update_value['$inc'].update({
                    f'answers.{answer_index}.count': 1
                })
                update_value['$set'].update({
                    f'answers.{answer_index}.time': cur_time
                })
                # ???????????????????????????raw_message ?????????????????????????????? push
                if self.chat_data.is_plain_text:
                    update_value['$push'] = {
                        f'answers.{answer_index}.messages': raw_message
                    }
            else:
                update_value['$push'] = {
                    'answers': {
                        'keywords': keywords,
                        'group_id': group_id,
                        'count': 1,
                        'time': cur_time,
                        'messages': [
                            raw_message
                        ]
                    }
                }

            context_mongo.update_one(find_key, update_value)
        else:
            context = {
                'keywords': pre_keywords,
                'time': cur_time,
                'count': 1,
                'answers': [
                    {
                        'keywords': keywords,
                        'group_id': group_id,
                        'count': 1,
                        'time': cur_time,
                        'messages': [
                            raw_message
                        ]
                    }
                ]
            }
            context_mongo.insert_one(context)

    def _context_find(self) -> Optional[Tuple[List[str], str]]:

        group_id = self.chat_data.group_id
        raw_message = self.chat_data.raw_message
        keywords = self.chat_data.keywords
        bot_id = self.chat_data.bot_id

        # ?????????
        if group_id in Chat._message_dict:
            group_msgs = Chat._message_dict[group_id]
            if len(group_msgs) >= Chat.repeat_threshold and \
                all(item['raw_message'] == raw_message
                    for item in group_msgs[:-Chat.repeat_threshold:-1]):
                # ???????????????????????????????????????
                group_bot_replies = Chat._reply_dict[group_id][bot_id]
                if len(group_bot_replies) and group_bot_replies[-1]['reply'] != raw_message:
                    return [raw_message, ], keywords
                else:
                    # ??????????????????????????????????????????
                    return None

        context = context_mongo.find_one({'keywords': keywords})

        if not context:
            return None

        if Chat._drunkenness_dict[group_id] > 0:
            answer_count_threshold = 1
        else:
            answer_count_threshold = Chat.answer_threshold

        if self.chat_data.to_me:
            cross_group_threshold = 1
        else:
            cross_group_threshold = Chat.cross_group_threshold

        ban_keywords = Chat._find_ban_keywords(
            context=context, group_id=group_id)

        candidate_answers = {}
        other_group_cache = {}
        answers_count = defaultdict(int)

        def candidate_append(dst, answer):
            answer_key = answer['keywords']
            if answer_key not in dst:
                dst[answer_key] = answer
            else:
                pre_answer = dst[answer_key]
                pre_answer['count'] += answer['count']
                pre_answer['messages'] += answer['messages']

        for answer in context['answers']:
            answer_key = answer['keywords']
            if answer_key in ban_keywords or answer['count'] < answer_count_threshold:
                continue

            sample_msg = answer['messages'][0]
            if self.chat_data.is_image and '[CQ:' not in sample_msg:
                # ????????????????????????????????????????????????????????????????????????????????????????????????
                continue

            if answer['group_id'] == group_id:
                candidate_append(candidate_answers, answer)
            # ???????????? at, ??????
            elif '[CQ:at,qq=' in sample_msg:
                continue
            else:   # ????????? N ???????????????????????????????????????????????????
                answers_count[answer_key] += 1
                cur_count = answers_count[answer_key]
                if cur_count < cross_group_threshold:      # ??????????????????????????????
                    candidate_append(other_group_cache, answer)
                elif cur_count == cross_group_threshold:   # ????????????????????????????????????
                    if cur_count > 1:
                        candidate_append(candidate_answers,
                                         other_group_cache[answer_key])
                    candidate_append(candidate_answers, answer)
                else:                                      # ????????????????????????
                    candidate_append(candidate_answers, answer)

        if not candidate_answers:
            return None

        final_answer = random.choices(list(candidate_answers.values()), weights=[
            # ?????????????????????????????????????????? Roll ?????????
            min(answer['count'], 10) for answer in candidate_answers.values()])[0]
        answer_str = random.choice(final_answer['messages'])
        answer_keywords = final_answer['keywords']

        if 0 < answer_str.count('???') <= 3 and random.random() < Chat.split_probability:
            return answer_str.split('???'), answer_keywords
        return [answer_str, ], answer_keywords

    @staticmethod
    def _text_to_speech(text: str) -> Optional[Message]:
        # if plugin_config.enable_voice:
        #     result = tts_client.synthesis(text, options={'per': 111})  # ?????????
        #     if not isinstance(result, dict):  # error message
        #         return MessageSegment.record(result)

        return Message(f'[CQ:tts,text={text}]')

    @staticmethod
    def update_global_blacklist() -> None:
        Chat._select_blacklist()

        keywords_dict = defaultdict(int)
        global_blacklist = set()
        for _, keywords_list in Chat.blacklist_answer.items():
            for keywords in keywords_list:
                keywords_dict[keywords] += 1
                if keywords_dict[keywords] == Chat.cross_group_threshold:
                    global_blacklist.add(keywords)

        Chat.blacklist_answer[Chat._blacklist_flag] |= global_blacklist

    @staticmethod
    def _select_blacklist() -> None:
        all_blacklist = blacklist_mongo.find()

        for item in all_blacklist:
            group_id = item['group_id']
            if 'answers' in item:
                Chat.blacklist_answer[group_id] |= set(item['answers'])
            if 'answers_reserve' in item:
                Chat.blacklist_answer_reserve[group_id] |= set(
                    item['answers_reserve'])

    @staticmethod
    def _sync_blacklist() -> None:
        Chat._select_blacklist()

        for group_id, answers in Chat.blacklist_answer.items():
            if not len(answers):
                continue
            blacklist_mongo.update_one(
                {'group_id': group_id},
                {'$set': {'answers': list(answers)}},
                upsert=True)

        for group_id, answers in Chat.blacklist_answer_reserve.items():
            if not len(answers):
                continue
            if group_id in Chat.blacklist_answer:
                answers = answers - Chat.blacklist_answer[group_id]

            blacklist_mongo.update_one(
                {'group_id': group_id},
                {'$set': {'answers_reserve': list(answers)}},
                upsert=True)

    @staticmethod
    def clearup_context() -> None:
        """
        ?????????????????? 30 ????????????????????????????????????
        """

        cur_time = int(time.time())
        expiration = cur_time - 30 * 24 * 3600  # ????????????

        context_mongo.delete_many({
            'time': {'$lt': expiration},
            'count': {'$lt': Chat.answer_threshold}    # lt ???????????????????????????
        })

        all_context = context_mongo.find({
            'count': {'$gt': 100},
            '$or': [
                # ????????????????????????????????????????????? clear_time ??????
                {"clear_time": {"$exists": False}},
                {"clear_time": {"$lt": expiration}}
            ]
        })
        for context in all_context:
            answers = [ans
                       for ans in context['answers']
                       # ????????????????????????????????????????????? answers.$.time ??????
                       if ans['count'] > 1 or ('time' in ans and ans['time'] > expiration)]
            context_mongo.update_one({
                'keywords': context['keywords']
            }, {
                '$set': {
                    'answers': answers,
                    'clear_time': cur_time
                }
            })

    @staticmethod
    def completely_sober():
        for key in Chat._drunkenness_dict.keys():
            Chat._drunkenness_dict[key] = 0

    @staticmethod
    def _find_ban_keywords(context, group_id) -> set:
        """
        ????????? group_id ???????????? context ????????????????????????
        """

        # ??????????????????
        ban_keywords = Chat.blacklist_answer[Chat._blacklist_flag] | Chat.blacklist_answer[group_id]
        # ??????????????????????????????
        if 'ban' in context:
            ban_count = defaultdict(int)
            for ban in context['ban']:
                ban_key = ban['keywords']
                if ban['group_id'] == group_id or ban['group_id'] == Chat._blacklist_flag:
                    ban_keywords.add(ban_key)
                else:
                    # ?????? N ????????????????????? ban ?????????????????? ban ???
                    ban_count[ban_key] += 1
                    if ban_count[ban_key] == Chat.cross_group_threshold:
                        ban_keywords.add(ban_key)
        return ban_keywords


# Auto sync on program start
Chat.update_global_blacklist()


def _chat_sync():
    Chat._sync()
    Chat._sync_blacklist()


# Auto sync on program exit
atexit.register(_chat_sync)


if __name__ == '__main__':

    # Chat.clearup_context()
    # # while True:
    test_data: ChatData = ChatData(
        group_id=1234567,
        user_id=1111111,
        raw_message='???????????????bug',
        plain_text='???????????????bug',
        time=time.time(),
        bot_id=0,
    )

    test_chat: Chat = Chat(test_data)

    print(test_chat.answer())
    test_chat.learn()

    test_answer_data: ChatData = ChatData(
        group_id=1234567,
        user_id=1111111,
        raw_message='???????????????bug',
        plain_text='???????????????bug',
        time=time.time(),
        bot_id=0,
    )

    test_answer: Chat = Chat(test_answer_data)
    print(test_chat.answer())
    test_answer.learn()

    # time.sleep(5)
    # print(Chat.speak())
