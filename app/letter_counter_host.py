import asyncio
import json
import os
from typing import List, Dict, Any  # 型ヒントのために追加
from openai import OpenAI

# OpenAI Chat Completion API の型をインポート
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
    ChatCompletionMessageToolCall,
)
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport
from dotenv import load_dotenv  # .env ファイル読み込み用に追加

# .env ファイルから環境変数を読み込む
load_dotenv()

# OpenAIのクライアントの準備
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# サーバースクリプトのパス (appディレクトリ内からの相対パス)
SERVER_SCRIPT = "./app/letter_counter.py"


# MCPサーバからツールスキーマを取得
async def get_tools():
    transport = PythonStdioTransport(script_path=SERVER_SCRIPT)
    async with Client(transport) as client:
        tools = await client.list_tools()
        return tools


# MCPサーバのツールを呼び出す
async def call_tool(tool_name: str, tool_args: Dict[str, Any]):  # 型ヒントを追加
    transport = PythonStdioTransport(script_path=SERVER_SCRIPT)
    async with Client(transport) as client:
        # fastmcpのcall_toolが返す型に合わせて調整が必要な場合がある
        result = await client.call_tool(tool_name, tool_args)
        return result


def main():
    # メッセージリストの準備 (ChatCompletionMessageParam を使用)
    messages: List[ChatCompletionMessageParam] = [
        {"role": "user", "content": "Strawberryに含まれるrの数は？"}
    ]

    # ツールの準備 (ChatCompletionToolParam を使用)
    mcp_tools = asyncio.run(get_tools())
    tools: List[ChatCompletionToolParam] = [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        }
        for tool in mcp_tools
    ]  # type: ignore
    print("ツール:", tools)

    # 推論の実行 (client.chat.completions.create を使用)
    response = client.chat.completions.create(
        model="gpt-4o", messages=messages, tools=tools
    )

    # 最初の応答メッセージを取得
    response_message = response.choices[0].message

    # ツール呼び出しがあるか確認
    tool_calls = response_message.tool_calls
    if tool_calls:
        # 最初のツール呼び出しを取得 (複数呼び出しはここでは考慮しない)
        # tool_call の型は ChatCompletionMessageToolCall
        tool_call: ChatCompletionMessageToolCall = tool_calls[0]
        if tool_call.type == "function":
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            result = asyncio.run(call_tool(tool_name, tool_args))
            print("関数呼び出し結果:", result)

            # メッセージリストにツール呼び出しと結果を追加
            # response_message (ChatCompletionMessage) を ChatCompletionAssistantMessageParam 形式の辞書に変換
            # role が 'assistant' であることを想定
            if response_message.tool_calls:
                # tool_calls がある場合
                assistant_message_dict = {
                    "role": "assistant",
                    "content": response_message.content,  # content は None の可能性あり
                    "tool_calls": response_message.tool_calls,
                }
            else:
                # tool_calls がない場合
                assistant_message_dict = {
                    "role": "assistant",
                    "content": response_message.content,  # content は None の可能性あり
                }

            # 型チェッカーのために明示的に型を指定する (やや冗長だがエラー回避のため)
            assistant_message: ChatCompletionMessageParam = assistant_message_dict  # type: ignore

            messages.append(assistant_message)

            tool_message: ChatCompletionMessageParam = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            }
            messages.append(tool_message)

            # 再度推論を実行
            response2 = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools,
            )
            # 応答メッセージの内容を取得
            final_content = response2.choices[0].message.content
            print("応答:", final_content if final_content else "応答がありませんでした")
        else:
            print(f"未対応のツール呼び出しタイプ: {tool_call.type}")
    else:
        # ツール呼び出しがない場合、最初のアシスタントの応答を表示
        final_content = response_message.content
        print("応答:", final_content if final_content else "応答がありませんでした")


if __name__ == "__main__":
    main()
