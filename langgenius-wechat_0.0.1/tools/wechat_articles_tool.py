# coding: utf-8
import json
import os
from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from wechatarticles import PublicAccountsWeb, ArticlesInfo


# 返回传入文件名的绝对路径
def get_file_path(filename: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


class WechatArticlesTool(Tool):
    def _parse_article_urls_response(self, article_data: list) -> dict:
        """解析获取文章链接的响应"""
        result = {
            "articles": [
                {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "update_time": item.get("update_time", 0),
                    "cover": item.get("cover", "")
                }
                for item in article_data
            ],
            "total_count": len(article_data)
        }
        return result

    def _parse_article_details_response(self, comments: list, read_num: int, like_num: int, old_like_num: int) -> dict:
        """解析获取文章详情的响应"""
        return {
            "comments": comments,
            "read_num": read_num,
            "like_num": like_num,
            "old_like_num": old_like_num
        }

    def _validate_common_parameters(self, tool_parameters: dict[str, Any]) -> list[str]:
        """验证通用参数"""
        errors = []
        required_params = [
            ('cookie', 'Cookie obtained from the WeChat official account platform'),
            ('token', 'Token obtained from the WeChat official account platform'),
            ('nickname', 'Nickname of the WeChat official account'),
            ('biz', 'Biz identifier of the WeChat official account')
        ]

        for param_name, description in required_params:
            if not tool_parameters.get(param_name):
                errors.append(f"Missing required parameter: {param_name}. {description}")

        # 验证count参数范围
        count = tool_parameters.get('count', 5)
        if not isinstance(count, int) or count < 1 or count > 5:
            errors.append("Parameter 'count' must be an integer between 1 and 5")

        return errors

    def _validate_details_parameters(self, tool_parameters: dict[str, Any]) -> list[str]:
        """验证获取文章详情的参数"""
        errors = []
        required_params = [
            ('appmsg_token', 'Appmsg_token obtained by capturing packets when opening WeChat official account articles'),
            ('wechat_cookie', 'Cookie obtained by capturing packets when opening WeChat official account articles'),
            ('article_url', 'URL of the WeChat official account article')
        ]

        for param_name, description in required_params:
            if not tool_parameters.get(param_name):
                errors.append(f"Missing required parameter for get_article_details: {param_name}. {description}")

        # 验证article_url格式
        article_url = tool_parameters.get('article_url')
        if article_url and not article_url.startswith('http'):
            errors.append("Parameter 'article_url' must be a valid URL")

        return errors

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        action = tool_parameters.get('action')
        begin = tool_parameters.get('begin', 0)
        count = tool_parameters.get('count', 5)

        # 验证操作类型
        if not action:
            yield self.create_text_message("Missing required parameter: action")
            return

        if action not in ['get_article_urls', 'get_article_details']:
            yield self.create_text_message(
                f'Invalid action: {action}. Supported actions are get_article_urls and get_article_details'
            )
            return

        # 验证通用参数
        common_errors = self._validate_common_parameters(tool_parameters)
        if common_errors:
            for error in common_errors:
                yield self.create_text_message(error)
            return

        try:
            cookie = tool_parameters['cookie']
            token = tool_parameters['token']
            nickname = tool_parameters['nickname']
            biz = tool_parameters['biz']

            if action == 'get_article_urls':
                # 获取文章链接
                paw = PublicAccountsWeb(cookie=cookie, token=token)
                article_data = paw.get_urls(nickname, biz=biz, begin=str(begin), count=str(count))
                valuable_res = self._parse_article_urls_response(article_data)
                yield self.create_json_message(valuable_res)
            elif action == 'get_article_details':
                # 验证获取文章详情的参数
                details_errors = self._validate_details_parameters(tool_parameters)
                if details_errors:
                    for error in details_errors:
                        yield self.create_text_message(error)
                    return

                appmsg_token = tool_parameters['appmsg_token']
                wechat_cookie = tool_parameters['wechat_cookie']
                article_url = tool_parameters['article_url']

                articles_info = ArticlesInfo(appmsg_token, wechat_cookie)
                comments = articles_info.comments(article_url)
                read_num, like_num, old_like_num = articles_info.read_like_nums(article_url)

                valuable_res = self._parse_article_details_response(comments, read_num, like_num, old_like_num)
                yield self.create_json_message(valuable_res)
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Network error occurred: {str(e)}")
        except ValueError as e:
            yield self.create_text_message(f"Invalid parameter value: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"An error occurred while invoking the tool: {str(e)}")