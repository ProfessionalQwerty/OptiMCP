"""Function-calling schema shapes for OpenAI and Anthropic."""

from optimcp.schemas import TOOL_NAME, anthropic_tool, openai_tool


def test_openai_tool_shape():
    tool = openai_tool()
    assert tool["type"] == "function"
    assert tool["function"]["name"] == TOOL_NAME
    assert tool["function"]["name"] == "check_consistency"
    assert isinstance(tool["function"]["parameters"], dict)
    assert "properties" in tool["function"]["parameters"]


def test_anthropic_tool_shape():
    tool = anthropic_tool()
    assert tool["name"] == "check_consistency"
    assert isinstance(tool["input_schema"], dict)
    assert "properties" in tool["input_schema"]
