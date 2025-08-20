from dify_plugin import Plugin, DifyPluginEnv
# from tools.wechat_articles_tool import WechatArticlesTool

# 初始化插件
plugin = Plugin(DifyPluginEnv())

# 注册工具
# plugin.register(WechatArticlesTool())

if __name__ == '__main__':
    plugin.run()