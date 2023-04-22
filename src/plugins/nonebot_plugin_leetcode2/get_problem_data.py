import httpx
import json
from pathlib import Path
from nonebot.log import logger



def get_random_title() -> str:
    '''请求随机题目'''
    try:
        get_random_data = httpx.post("https://leetcode-cn.com/graphql", json={
            "query": "query problemsetRandomFilteredQuestion($categorySlug: String!, $filters: QuestionListFilterInput) {  problemsetRandomFilteredQuestion(categorySlug: $categorySlug, filters: $filters)}",
            "variables": {
                "categorySlug": "",
                "filters": {}
            }
        })
        random_data = json.loads(get_random_data.text)
        titleSlug = random_data["data"]["problemsetRandomFilteredQuestion"]
        return titleSlug
    except Exception as e:
        logger.error("[LC查询] 获取随机题目标题时出错。",e)
        raise e


def get_today_title() -> str:
    '''获取今日的每日一题标题'''
    try:
        get_today_data = httpx.post("https://leetcode-cn.com/graphql", json={
            "query":"query questionOfToday {todayRecord { date question {frontendQuestionId: questionFrontendId difficulty titleSlug } } } ",
            "variables":{}
            })
        today_data = json.loads(get_today_data.text)
        titleSlug = today_data["data"]["todayRecord"][0]["question"]["titleSlug"]
        return titleSlug
    except Exception as e:
        logger.error("[LC查询] 获取每日一题标题时出错。",e)
        raise e


def get_search_title(keyword) -> str:
    '''调用查询接口进行查询，返回首个查询结果题目标题'''
    try:
        get_search_data = httpx.post("https://leetcode-cn.com/graphql", json={
            "query": "query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {  problemsetQuestionList(    categorySlug: $categorySlug    limit: $limit    skip: $skip    filters: $filters  ) {    hasMore    total    questions {      acRate      difficulty      freqBar      frontendQuestionId      isFavor      paidOnly      solutionNum      status      title      titleCn      titleSlug      topicTags {        name        nameTranslated        id        slug      }      extra {        hasVideoSolution        topCompanyTags {          imgUrl          slug          numSubscribed        }      }    }  }}    ",
            "variables": {
                "categorySlug": "",
                "skip": 0,
                "limit": 1,
                "filters": {
                    "searchKeywords": keyword
                }
            }
        })
        search_data = json.loads(get_search_data.text)
        question_list = search_data["data"]["problemsetQuestionList"]["questions"]
        if question_list:
            titleSlug = question_list[0]["titleSlug"]
        else:
            titleSlug = ""
        return titleSlug
    except Exception as e:
        logger.error("[LC查询] 获取搜索标题时出错。",e)
        raise e


def get_sub_problem_data(titleSlug) -> list:
    '''获取某一已知名称的题目内容'''
    try:
        with open(Path(__file__).parent / "template" / "template.html", "r", encoding="UTF-8") as f:
            html_template = f.read()
    except Exception as e:
        logger.error("[LC查询] 载入HTML模板时发生错误。",e)
        raise e
    try:
        get_problem_data = httpx.post("https://leetcode-cn.com/graphql", json={
            "operationName": "questionData",
            "variables": {
                "titleSlug": titleSlug },
            "query": "query questionData($titleSlug: String!) { question(titleSlug: $titleSlug) { questionFrontendId title titleSlug translatedTitle translatedContent difficulty } } "
            })
        problem_data = json.loads(get_problem_data.text)
        problem_data = problem_data["data"]["question"]
        #题目信息（题号+题目译名）
        problem_title = problem_data.get("questionFrontendId")+"."+problem_data.get("translatedTitle")
        #题目难度（英语单词）
        problem_difficulty = "题目难度："+problem_data.get("difficulty")
        #题目内容（用html输出）
        problem_content:str = problem_data.get("translatedContent")
        problem_content = html_template.replace("【content】",(problem_content.replace('\\"', '"'))).replace("【title】", problem_title)
        #题目链接
        problem_link = "本题链接："+f"https://leetcode-cn.com/problems/{titleSlug}/" 
        return [problem_title, problem_difficulty, problem_content, problem_link]
    except Exception as e:
        logger.error("[LC查询] 获取已知题目的内容时出错。",e)
        raise e