import pandas as pd

from .startand import NUMBER_MAP, SAVE_MAP


async def df_to_guoguanlv(df: pd.DataFrame):
    """分析救援关过图率"""
    data = df[df["游戏模式"] == "AnneHappy药役"]
    other = df[df["游戏模式"].isin(["牛牛冲刺", "单人装逼"])]
    all_map = len(data["地图"])
    other_map = len(other["地图"])
    resen = 0
    last_maps = {}
    for m in SAVE_MAP:
        prefix = m.split("m")[0]
        if prefix in last_maps:
            last_maps[prefix] = max(last_maps[prefix], m)
        else:
            last_maps[prefix] = m

    map_counts = {}

    n = 0
    for key in last_maps:
        count = len(data[data["地图"].str.startswith(key)])
        if count == 0:
            continue
        last_map = last_maps[key]
        map_count = len(data[data["地图"] == last_map])
        map_counts[key] = map_count * NUMBER_MAP[n] / count
        quan = count / all_map
        resen += quan * map_counts[key]
        n += 1

    # result = []
    # for i in range(1, 15):
    #     key = 'c{}'.format(i)
    #     if key in map_counts:
    #         result.append('{}:{}%'.format(key, round(map_counts[key] * 100)))

    # print(result)
    # result = '救援图过关率: {:.2%}'.format(resen)

    # 加上特殊关卡
    try:
        resen += other_map / (all_map + other_map)
        result = {"救援关": str("{:.2%}".format(resen))}
    except (TypeError, KeyError):
        result = {"救援关": "错误"}
    except ZeroDivisionError:
        result = {"救援关": "0.00%"}
    except:
        result = {"救援关": "错误"}
    return result
