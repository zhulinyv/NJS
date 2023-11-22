def is_valid_name(s):
    count = 0
    for c in s:
        if c.isalnum() or (c in ["_", "-"]):
            count += 1
        else:
            raise Exception("chat_name 会话名称 只能由数字,字母,汉字,'_','-' 组成")
        if count > 10:
            raise Exception("chat_name 会话名称 中的字符数量不能多于10个")
    return True
