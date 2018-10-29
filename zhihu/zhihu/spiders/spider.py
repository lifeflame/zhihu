# -*- coding:utf-8 -*-

import json
from scrapy import Spider,Request
from ..items import UserItem

class ZhihuSpider(Spider):
    name = "zhihu"
    #定义允许爬取的域名
    allowed_domains = ["www.zhihu.com"]
    #用户列表的url
    user_url = "https://www.zhihu.com/api/v4/members/{user}?include={include}"
    #大v关注他人的url
    followee_url = "https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}" \
                   "&limit={limit}"
    #别人关注大v的url
    follower_url = "https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}" \
                   "&limit={limit}"
    #最开始爬取的url，即大v本人的url
    start_user = "excited-vczh"
    user_query = "allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count," \
                 "articles_count,gender,badge[?(type=best_answerer)].topics"
    followee_query = "data[*].answer_count,articles_count,gender,follower_count,is_followed," \
                     "is_following,badge[?(type=best_answerer)].topics"
    follower_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,' \
                      'badge[?(type=best_answerer)].topics'

    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user,include=self.user_query),callback=self.parse_user)
        yield Request(self.followee_url.format(user=self.start_user,include=self.followee_query,offset=0,limit=20),
                      callback=self.parse_followee)
        yield Request(self.follower_url.format(user=self.start_user,include=self.follower_query,limit=20,offset=0)
                      ,callback=self.parse_follower)

    def parse_user(self,response):
        result = json.loads(response.text)
        item = UserItem()
        for field in item.fields:
            #判断item中声明的是否在result存在，若存在，就保存下来
            if field in result.keys():
                item[field] = result.get(field)
            yield item
            yield Request(self.followee_url.format(user=result.get("url_token"),include=self.followee_query,limit=20
                                               ,offset=0),callback=self.parse_followee)
            yield Request(self.follower_url.format(user=result.get("url_token"),include=self.followee_query,limit=20
                                               ,offset=0),callback=self.parse_follower)

    def parse_followee(self,response):
        results = json.loads(response.text)
        if "data" in results.keys():
            for result in results.get("data"):
                yield Request(self.user_url.format(user=result.get("url_token"),include=self.user_query),self.parse_user)
        if "paging" in results.keys() and results.get("paging").get("is_end") is False:
            next_page = results.get("paging").get("next")
            yield Request(next_page,callback=self.parse_followee)

    def parse_follower(self,response):
        results = json.loads(response.text)
        if "data" in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query)
                              , self.parse_user)

            if 'paging' in results.keys() and results.get('paging').get('is_end') is False:
                next_page = results.get('paging').get('next')
                yield Request(next_page,self.parse_follower)


