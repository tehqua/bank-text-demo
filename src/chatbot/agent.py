import json
import re
from src.chatbot.ollama_client import OllamaClient
from src.chatbot.tools import ChatbotTools, TOOLS_DEFINITION
from src.utils.logger import default_logger as logger

SYSTEM_PROMPT = """Bạn là AI Assistant chuyên phân tích feedback/comment ngân hàng.

Bạn có quyền truy cập các công cụ sau:
{tools}

Khi người dùng yêu cầu, hãy sử dụng công cụ phù hợp.

Để sử dụng công cụ, trả lời theo format JSON:
```json
{{
  "tool": "tên_công_cụ",
  "parameters": {{
    "param1": "value1"
  }}
}}
```

Nếu không cần dùng công cụ, hãy trả lời trực tiếp bằng tiếng Việt.

Bạn giúp người dùng:
- Truy vấn và phân tích data comments
- Xem thống kê tổng quan
- Tìm issues/vấn đề tiêu cực
- Kiểm tra anomalies
- Quản lý models (xóa để retrain)

Hãy thân thiện, hữu ích và chính xác."""

class ChatbotAgent:
    def __init__(self, df_pandas=None, model="llama3.2:3b"):
        self.ollama = OllamaClient(model=model)
        self.tools = ChatbotTools(df_pandas)
        self.conversation_history = []

    def update_data(self, df_pandas):
        self.tools.df_pandas = df_pandas

    def _format_tools_for_prompt(self):
        tools_str = ""
        for tool in TOOLS_DEFINITION:
            tools_str += f"\n- {tool['name']}: {tool['description']}"
            if tool['parameters']:
                tools_str += f"\n  Parameters: {tool['parameters']}"
        return tools_str

    def _extract_tool_call(self, response):
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                tool_call = json.loads(json_match.group(1))
                if "tool" in tool_call:
                    return tool_call
            except json.JSONDecodeError:
                pass

        direct_json_match = re.search(r'\{[\s\S]*"tool"[\s\S]*\}', response)
        if direct_json_match:
            try:
                tool_call = json.loads(direct_json_match.group(0))
                if "tool" in tool_call:
                    return tool_call
            except json.JSONDecodeError:
                pass

        return None

    def chat(self, user_message):
        if not self.ollama.is_available():
            return "⚠️ Ollama không khả dụng. Vui lòng cài đặt và chạy Ollama trước.\n\nHướng dẫn:\n1. Download Ollama: https://ollama.com/download\n2. Chạy: ollama pull llama3.2:3b\n3. Ollama sẽ tự động chạy ở background"

        system_msg = SYSTEM_PROMPT.format(tools=self._format_tools_for_prompt())

        messages = [{"role": "system", "content": system_msg}]

        for msg in self.conversation_history[-6:]:
            messages.append(msg)

        messages.append({"role": "user", "content": user_message})

        response = self.ollama.chat(messages, temperature=0.3)

        if response is None:
            return "❌ Lỗi kết nối với Ollama. Vui lòng kiểm tra lại."

        tool_call = self._extract_tool_call(response)

        if tool_call:
            tool_name = tool_call.get("tool")
            parameters = tool_call.get("parameters", {})

            logger.info(f"Tool call: {tool_name} with params: {parameters}")

            tool_result = self.tools.execute_tool(tool_name, parameters)

            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": f"Tool result: {tool_result}"})

            final_response = self.ollama.chat(messages, temperature=0.3)

            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": final_response})

            return final_response

        else:
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": response})

            return response

    def clear_history(self):
        self.conversation_history = []
