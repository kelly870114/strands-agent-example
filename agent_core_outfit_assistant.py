#!/usr/bin/env python3
"""
# 👗 AgentCore + Strands 穿搭助手

結合 AWS Bedrock AgentCore 和 Strands Agents 的智能穿搭顧問
提供個性化的服裝建議，整合天氣資訊和記憶功能

## 功能特色

- **AgentCore 整合**: 使用 AWS Bedrock AgentCore 進行 agent 管理
- **Strands Agent**: 保持原有的 Strands 功能和工具
- **智能記憶**: 使用 Mem0 記住用戶偏好
- **天氣整合**: 根據天氣條件提供建議
- **個性化建議**: 基於場合、風格、個人喜好

## 環境設定

```bash
export MEM0_API_KEY="your_mem0_api_key"
export OPENWEATHER_API_KEY="your_openweather_api_key"
export USER_ID="your_name"
```
"""

import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from strands import Agent
from strands_tools import http_request, mem0_memory

# AgentCore 相關導入 (基於 AWS Bedrock AgentCore)
try:
    from bedrock_agent_core import AgentCore, AgentConfig, ToolRegistry
    from bedrock_agent_core.models import BedrockModel
    AGENTCORE_AVAILABLE = True
except ImportError:
    print("⚠️  AgentCore 不可用，使用純 Strands Agent 模式")
    AGENTCORE_AVAILABLE = False

# 配置 - 從環境變數讀取 API Key 和用戶 ID
MEM0_API_KEY = os.getenv('MEM0_API_KEY')
USER_ID = os.getenv('USER_ID', 'current_user')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

# 檢查必要的 API Keys
if not MEM0_API_KEY:
    print("⚠️  警告：MEM0_API_KEY 環境變數未設定，記憶功能可能無法正常運作")
if not OPENWEATHER_API_KEY:
    print("⚠️  警告：OPENWEATHER_API_KEY 環境變數未設定，天氣功能將無法使用")

# 設定 Mem0 環境變數（如果有的話）
if MEM0_API_KEY:
    os.environ['MEM0_API_KEY'] = MEM0_API_KEY

# 專業時尚顧問系統提示
OUTFIT_CONSULTANT_PROMPT = f"""
你是專業的私人穿搭顧問 Ginny, 10 年時尚造型經驗。你的特色是：

🎯 **諮詢風格**：
- 一定會先問使用者的名字
- 像真正的造型師一樣，主動詢問關鍵資訊
- 友善、專業，但不會過於正式
- 給出具體可行的建議，不只是抽象概念

💭 **智能建議策略**：
在回應用戶時，總是先使用 mem0_memory 工具查詢該用戶的歷史偏好和資訊。
當資訊不足時，你會主動詢問：
1. **場合**：工作會議、約會、休閒、特殊活動？
2. **地點與時間**：哪個城市？什麼時候？
3. **個人風格**：簡約、優雅、休閒、前衛？
4. **特殊需求**：舒適度、預算、身型考量？

基於豐富的時尚知識，結合天氣資訊，提供專業的穿搭建議。
如需最新流行趨勢，可以使用 http_request 查詢時尚 API。

🔧 **使用工具**：
- **查天氣**：使用 http_request 呼叫 OpenWeatherMap API
  - 當前天氣：http://api.openweathermap.org/data/2.5/weather?q={{city}}&appid={{OPENWEATHER_API_KEY}}&units=metric&lang=zh_tw
  - 5天預報：http://api.openweathermap.org/data/2.5/forecast?q={{city}}&appid={{OPENWEATHER_API_KEY}}&units=metric&lang=zh_tw
- **搜尋趨勢**：使用 http_request 調用搜尋 API 或給出基於知識的建議
- **記住偏好**：使用 mem0_memory 儲存和回憶用戶偏好，當使用者說他的名字後，就要記錄他的穿搭喜好，並且存入 mem0 的 User ID 會是他的名字。

注意：免費版本可以查詢未來5天的天氣預報，每3小時一次更新。

📝 **建議格式**：
- 具體的服裝單品（上衣、下身、外套、鞋子）
- 顏色搭配建議
- 材質選擇（考慮天氣）
- 配件點綴
- 實用的穿搭小技巧

🎨 **回應風格**：
- 使用 emoji 讓對話更生動
- 解釋選擇理由
- 提供替代方案
- 考慮實用性和美觀度

記住：每次對話都是一次專業的造型諮詢！
"""


class AgentCoreOutfitAssistant:
    """
    結合 AgentCore 和 Strands 的穿搭助手類別
    """
    
    def __init__(self):
        self.user_id = USER_ID
        self.openweather_api_key = OPENWEATHER_API_KEY
        
        if AGENTCORE_AVAILABLE:
            self._initialize_agentcore()
        else:
            self._initialize_strands_only()
    
    def _initialize_agentcore(self):
        """初始化 AgentCore 模式"""
        print("🔧 初始化 AgentCore + Strands 模式...")
        
        # 創建 AgentCore 配置
        agent_config = AgentConfig(
            name="outfit_consultant",
            description="專業穿搭顧問，提供個性化服裝建議",
            model_config={
                "provider": "bedrock",
                "model_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                "temperature": 0.7
            },
            system_prompt=OUTFIT_CONSULTANT_PROMPT
        )
        
        # 註冊工具到 AgentCore
        tool_registry = ToolRegistry()
        tool_registry.register_tool("mem0_memory", mem0_memory)
        tool_registry.register_tool("http_request", http_request)
        
        # 初始化 AgentCore
        self.agent_core = AgentCore()
        
        # 創建 Strands Agent 並註冊到 AgentCore
        self.strands_agent = Agent(
            system_prompt=OUTFIT_CONSULTANT_PROMPT,
            tools=[http_request, mem0_memory]
        )
        
        # 將 Strands Agent 註冊到 AgentCore
        self.agent_core.register_agent(
            agent_id="outfit_consultant",
            agent=self.strands_agent,
            config=agent_config
        )
        
        print("✅ AgentCore + Strands 初始化完成！")
    
    def _initialize_strands_only(self):
        """初始化純 Strands 模式（後備方案）"""
        print("🔧 初始化純 Strands Agent 模式...")
        
        # 創建 Strands Agent
        self.strands_agent = Agent(
            system_prompt=OUTFIT_CONSULTANT_PROMPT,
            tools=[http_request, mem0_memory]
        )
        
        print("✅ Strands Agent 初始化完成！")
    
    def get_outfit_advice(self, user_input):
        """
        獲取穿搭建議
        
        Args:
            user_input (str): 用戶的穿搭需求
            
        Returns:
            str: 穿搭建議回應
        """
        try:
            if AGENTCORE_AVAILABLE:
                # 使用 AgentCore 執行
                response = self.agent_core.execute_agent(
                    agent_id="outfit_consultant",
                    input_data=user_input,
                    context={"user_id": self.user_id}
                )
                return response.get("output", "抱歉，無法獲取回應")
            else:
                # 使用純 Strands Agent
                response = self.strands_agent(user_input, user_id=self.user_id)
                return str(response)
                
        except Exception as e:
            return f"❌ 發生錯誤: {str(e)}"
    
    def demo_conversation(self):
        """展示對話能力"""
        print("\n🎬 實際展示 AgentCore + Strands 智能對話能力！")
        print("=" * 60)
        print("💡 讓我們看看 AI 如何從零開始，像真正的造型師一樣：")
        print("   • 主動提問了解需求")
        print("   • 記住您的偏好") 
        print("   • 提供個性化建議")
        print("\n🎯 建議試試這些開場：")
        print("   「我需要穿搭建議」")
        print("   「明天要去約會」")
        print("   「幫我搭配上班服裝」")
        
        self.interactive_session()
    
    def interactive_session(self):
        """互動式對話會話"""
        print("\n💬 開始與 Ginny 對話...")
        print("💡 小提示：你可以說「我明天要去約會」、「幫我搭配上班服裝」等")
        print("輸入 'exit' 結束對話\n")
        
        while True:
            try:
                user_input = input("👤 您: ")
                
                if user_input.lower() in ['exit', '退出', 'bye']:
                    print("\n👗 Ginny: 很高興為您服務！期待下次為您搭配美美的造型！ 👋")
                    break
                
                if not user_input.strip():
                    continue
                    
                print("\n👗 Ginny: ", end="", flush=True)
                response = self.get_outfit_advice(user_input)
                print(f"{response}")
                print()
                
            except KeyboardInterrupt:
                print("\n\n👗 Ginny: 下次見！記得穿美美的哦~ 👋")
                break
            except Exception as e:
                print(f"\n❌ 發生錯誤: {str(e)}")
                print("請再試一次，或輸入 'exit' 結束對話")
    
    def show_help(self):
        """顯示幫助資訊"""
        print("""
👗 AgentCore + Strands 智能穿搭助手 Ginny

✨ 功能特色：
• 🤖 AgentCore 整合：企業級 agent 管理
• 🧠 智能對話：主動詢問關鍵資訊
• 🌤️  天氣整合：根據天氣條件推薦
• 🧠 記憶學習：記住您的穿搭偏好  
• 🔍 流行趨勢：搜尋最新時尚資訊
• 💼 場合適配：工作、約會、休閒等不同場景

💬 對話範例：
• "我明天要去約會，該穿什麼？"
• "下週有重要會議，幫我搭配正式一點的服裝"
• "今天天氣這麼熱，有什麼清爽的穿搭建議？"
• "我想要簡約風格的週末穿搭"

🎯 Ginny 會主動詢問：
• 具體場合和重要程度
• 地點和天氣需求
• 您的風格偏好
• 特殊需求或限制

🔧 技術架構：
• AgentCore: AWS Bedrock 企業級 agent 框架
• Strands Agent: 先進的對話 AI 技術
• Mem0: 長期記憶管理
• OpenWeather API: 即時天氣資訊
""")


def main():
    """主程式入口"""
    print("👗 AgentCore + Strands 智能穿搭助手 Ginny")
    print("=" * 60)
    print("🌟 結合企業級 AgentCore 與 Strands 技術的穿搭顧問！")
    print("🧠 已啟用 Mem0 記憶功能 - 會記住您的偏好！")
    
    if not OPENWEATHER_API_KEY:
        print("\n⚠️  提醒：請設定 OPENWEATHER_API_KEY 環境變數以啟用天氣功能")
        print("免費申請：https://openweathermap.org/api")
    else:
        print("🌤️  天氣 API 已準備就緒！")
    
    # 初始化穿搭助手
    assistant = AgentCoreOutfitAssistant()
    
    print("\n選項：")
    print("  'demo' - 開始實際展示（推薦）")
    print("  'chat' - 一般互動模式")
    print("  'help' - 查看詳細說明") 
    print("  'exit' - 結束程式")
    
    while True:
        try:
            choice = input("\n📝 請選擇操作 (直接按 Enter 開始 demo): ").lower().strip()
            
            if choice == 'exit':
                print("\n👋 再見！")
                break
            elif choice == 'demo' or choice == '':
                assistant.demo_conversation()
            elif choice == 'chat':
                assistant.interactive_session()
            elif choice == 'help':
                assistant.show_help()
            else:
                print("❓ 請輸入有效選項：demo, chat, help, exit")
                
        except KeyboardInterrupt:
            print("\n\n👋 程式已結束！")
            break
        except Exception as e:
            print(f"\n❌ 發生錯誤: {str(e)}")
            print("請再試一次")


if __name__ == "__main__":
    main()