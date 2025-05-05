from fastmcp import FastMCP

mcp = FastMCP("Letter Counter")


@mcp.tool()
def letter_counter(word: str, letter: str) -> int:
    """
    単語の中に文字が何回現れるかを数える。

    Args:
        word: 分析する単語またはフレーズ
        letter: 出現回数を数える文字

    Returns:
        単語中にその文字が現れる回数
    """
    return word.lower().count(letter.lower())


if __name__ == "__main__":
    mcp.run(transport="stdio")
