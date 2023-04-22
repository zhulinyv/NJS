import httpx
import json
from nonebot.log import logger



def get_user_public_profile(userSlug):
    '''获取用户公开信息'''
    try:
        get_data = httpx.post("https://leetcode-cn.com/graphql", json={
            "operationName": "userPublicProfile",
            "variables": {
                "userSlug": userSlug
            },
            "query": "query userPublicProfile($userSlug: String!) {  userProfilePublicProfile(userSlug: $userSlug) {    username    haveFollowed    siteRanking    profile {      userSlug      realName      aboutMe      userAvatar      location      gender      websites      skillTags      contestCount      asciiCode      medals {        name        year        month        category        __typename      }      ranking {        rating        ranking        currentLocalRanking        currentGlobalRanking        currentRating        ratingProgress        totalLocalUsers        totalGlobalUsers        __typename      }      skillSet {        langLevels {          langName          langVerboseName          level          __typename        }        topics {          slug          name          translatedName          __typename        }        topicAreaScores {          score          topicArea {            name            slug            __typename          }          __typename        }        __typename      }      socialAccounts {        provider        profileUrl        __typename      }      __typename    }    educationRecordList {      unverifiedOrganizationName      __typename    }    occupationRecordList {      unverifiedOrganizationName      jobTitle      __typename    }    submissionProgress {      totalSubmissions      waSubmissions      acSubmissions      reSubmissions      otherSubmissions      acTotal      questionTotal      __typename    }    __typename  }}"
        })
        user_public_data = json.loads(get_data.text)
        return user_public_data
    except Exception as e:
        logger.error("[LC查询] 获取用户公开信息时出错。",e)
        raise e



def get_user_question_progress(userSlug):
    '''获取用户已通过题目'''
    try:
        get_data = httpx.post("https://leetcode-cn.com/graphql", json={
            "operationName": "userQuestionProgress",
            "variables": {
                "userSlug": userSlug
            },
            "query": "query userQuestionProgress($userSlug: String!) {  userProfileUserQuestionProgress(userSlug: $userSlug) {    numAcceptedQuestions {      difficulty      count      __typename    }    numFailedQuestions {      difficulty      count      __typename    }    numUntouchedQuestions {      difficulty      count      __typename    }    __typename  }}"
        })
        user_question_progress = json.loads(get_data.text)
        return user_question_progress
    except Exception as e:
        logger.error("[LC查询] 获取用户已通过题目时出错。",e)
        raise e



def get_user_solution_count(userSlug):
    '''获取用户已发布题解数'''
    try:
        get_data = httpx.post("https://leetcode-cn.com/graphql", json={
            "operationName": "columnsUserSolutionCount",
            "variables": {
                "userSlug": userSlug
            },
            "query": "query columnsUserSolutionCount($userSlug: String!) {\n  columnsUserSolutionCount(userSlug: $userSlug)\n}\n"
        })
        user_solution_count = json.loads(get_data.text)
        return user_solution_count
    except Exception as e:
        logger.error("[LC查询] 获取用户已发布题解数时出错。",e)
        raise e



def get_user_profile_articles(userSlug):
    '''获取用户最新题解题目'''
    try:
        get_data = httpx.post("https://leetcode-cn.com/graphql", json={
            "operationName": "profileArticles",
            "variables": {
                "userSlug": userSlug,
                "skip": 0,
                "first": 15
            },
            "query": "query profileArticles($userSlug: String!, $skip: Int, $first: Int) {\n  solutionArticles(userSlug: $userSlug, skip: $skip, first: $first) {\n    edges {\n      node {\n        title\n        slug\n        question {\n          title\n          titleSlug\n          translatedTitle\n          questionFrontendId\n          __typename\n        }\n        upvoteCount\n        topic {\n          commentCount\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
        })
        user_profile_articles = json.loads(get_data.text)
        return user_profile_articles
    except Exception as e:
        logger.error("[LC查询] 获取用户最新题解时出错。",e)
        raise e



def get_user_community_achievement(userSlug):
    '''获取用户声望信息'''
    try:
        get_data = httpx.post("https://leetcode-cn.com/graphql", json={
            "operationName": "profileCommunityAchievement",
            "variables": {
                "userSlug": userSlug,
                "size": 3
            },
            "query": "query profileCommunityAchievement($size: Int!, $userSlug: String!) {\n  profileCommunityAchievement(size: $size, userSlug: $userSlug) {\n    date\n    voteCount\n    viewCount\n    favoriteCount\n    __typename\n  }\n}\n"
        })
        user_community_achievement = json.loads(get_data.text)
        return user_community_achievement
    except Exception as e:
        logger.error("[LC查询] 获取用户声望信息时出错。",e)
        raise e



def get_user_question_submitstats(userSlug):
    '''获取用户题目提交统计'''
    try:
        get_data = httpx.post("https://leetcode-cn.com/graphql", json={
            "operationName": "userQuestionSubmitStats",
            "variables": {
                "userSlug": userSlug
            },
            "query": "query userQuestionSubmitStats($userSlug: String!) {\n  userProfileUserQuestionSubmitStats(userSlug: $userSlug) {\n    acSubmissionNum {\n      difficulty\n      count\n      __typename\n    }\n    totalSubmissionNum {\n      difficulty\n      count\n      __typename\n    }\n    __typename\n  }\n}\n"
        })
        user_question_submitstat = json.loads(get_data.text)
        return user_question_submitstat
    except Exception as e:
        logger.error("[LC查询] 获取用户题目提交统计时出错。",e)
        raise e



def get_user_medals(userSlug):
    '''获取用户勋章'''
    try:
        get_data = httpx.post("https://leetcode-cn.com/graphql", json={
            "operationName": "userMedals",
            "variables": {
                "userSlug": userSlug
            },
            "query": "query userMedals($userSlug: String!) {\n  userProfileUserMedals(userSlug: $userSlug) {\n    ...medalNodeFragment\n    __typename\n  }\n  userProfileUserLevelMedal(userSlug: $userSlug) {\n    current {\n      ...medalNodeFragment\n      __typename\n    }\n    next {\n      ...medalNodeFragment\n      __typename\n    }\n    __typename\n  }\n  userProfileUserNextMedal(userSlug: $userSlug) {\n    ...medalNodeFragment\n    __typename\n  }\n}\n\nfragment medalNodeFragment on MedalNodeV2 {\n  name\n  obtainDate\n  category\n  config {\n    icon\n    iconGif\n    iconGifBackground\n    __typename\n  }\n  progress\n  id\n  year\n  month\n  __typename\n}\n"
        })
        user_medals = json.loads(get_data.text)
        return user_medals
    except Exception as e:
        logger.error("[LC查询] 获取用户勋章信息时出错。",e)
        raise e