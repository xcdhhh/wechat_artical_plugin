from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class WechatArticlesProvider(ToolProvider):
    def __init__(self):
        super().__init__()

    def validate_credentials(self, credentials: dict) -> None:
        # No credentials required for WeChat Articles tool
        pass

    def get_tool_definitions(self) -> list:
        return super().get_tool_definitions()

    def invoke_tool(self, tool_name: str, params: dict) -> dict:
        return super().invoke_tool(tool_name, params)