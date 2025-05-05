# my_server.py
from fastmcp import FastMCP

mcp = FastMCP(
    name="ConfiguredServer",
    port=8080,  # ServerSettingsに直接マップ
    on_duplicate_tools="error",  # 重複処理を設定
)

# 設定はmcp.settingsからアクセスできる
print(mcp.settings.port)  # 出力: 8080
print(mcp.settings.on_duplicate_tools)  # 出力: "error"


@mcp.tool()
def greet(name: str) -> str:
    """ユーザーの名前であいさつ"""
    return f"Hello, {name}!"


if __name__ == "__main__":
    # このコードはファイルが直接実行された場合にのみ実行される

    # デフォルト設定での基本実行（stdioトランスポート）
    mcp.run()

    # 特定のトランスポートとパラメータの使用
    # mcp.run(transport="sse", host="127.0.0.1", port=9000)
