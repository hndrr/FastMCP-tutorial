import asyncio
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport


async def main():
    # サーバースクリプトのパス (appディレクトリ内からの相対パス)
    server_script = "./app/letter_counter.py"

    # PythonStdioTransportを使用してサーバを起動
    transport = PythonStdioTransport(script_path=server_script)

    # クライアントを作成し、サーバと通信
    async with Client(transport) as client:
        # 利用可能なツールを取得
        tools = await client.list_tools()
        print("ツール:", tools)

        # ツールの呼び出し
        result = await client.call_tool(
            "letter_counter", {"word": "Strawberry", "letter": "r"}
        )
        print("ツール呼び出し結果:", result)


if __name__ == "__main__":
    asyncio.run(main())
