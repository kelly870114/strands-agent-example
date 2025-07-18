#!/usr/bin/env python3
"""
Strands Agent 穿搭助手
"""

import streamlit as st
import os
import warnings
import time
import threading
from queue import Queue
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
warnings.filterwarnings("ignore", category=DeprecationWarning)

from strands import Agent
from strands_tools import http_request, mem0_memory

# 頁面配置
st.set_page_config(
    page_title=" Strands Agent 穿搭助理",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
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
################### Prompt ###################

# Professional fashion consultant system prompt
OUTFIT_CONSULTANT_PROMPT = f"""
你是專業的私人穿搭顧問 Strands, 10 年時尚造型經驗。你的特色是：

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
  - 當前天氣：http://api.openweathermap.org/data/2.5/weather?q={{city}}&appid={OPENWEATHER_API_KEY}&units=metric&lang=zh_tw
  - 5天預報：http://api.openweathermap.org/data/2.5/forecast?q={{city}}&appid={OPENWEATHER_API_KEY}&units=metric&lang=zh_tw
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

##############################################

################### Strands Agent ###################
@st.cache_resource
def create_outfit_agent():
    """創建並緩存 outfit agent"""
    return Agent(
        system_prompt=OUTFIT_CONSULTANT_PROMPT,
        tools=[http_request, mem0_memory]
    )

# 創建 agent
outfit_agent = create_outfit_agent()

#####################################################

# 自定義 CSS 樣式
st.markdown("""
<style>
    .main-header {
        background: #FF9900;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .debug-header {
        color: #ff6b6b;
        font-weight: bold;
    }
    
    .tool-output {
        background: #1e1e1e;
        color: #00ff00;
        padding: 10px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
    }
    
    .typing-cursor {
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
</style>
""", unsafe_allow_html=True)

# 主標題
st.markdown('<h1 class="main-header"> Strands Agent 穿搭助手 </h1>', unsafe_allow_html=True)

# 初始化對話歷史和工具調用歷史
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_calls" not in st.session_state:
    st.session_state.tool_calls = []

# 如果是第一次訪問，顯示歡迎訊息
if len(st.session_state.messages) == 0:
    welcome_message = """
    👋 **歡迎！我是您的私人穿搭顧問 Strands**
    
    🔧 **此 Streamlit Demo 特色**：
    • 💕 完整的工具調用過程顯示
    • 🔍 實時監控 API 調用
    • 📊 記憶系統狀態追蹤
    • 🌤️ 天氣 API 調用詳情
    
    告訴我您的需求，讓我為您打造專屬造型！
    """
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})

# 主要內容區域
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 對話區域")
    
    # 顯示對話歷史
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"], avatar="👗" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])
            
            # 如果有對應的工具調用，顯示
            if message["role"] == "assistant" and i < len(st.session_state.tool_calls):
                tool_call = st.session_state.tool_calls[i]
                if tool_call:
                    with st.expander("🔧 工具調用詳情", expanded=False):
                        st.markdown("**調用的工具：**")
                        for tool_name, tool_info in tool_call.items():
                            st.markdown(f"• **{tool_name}**")
                            if tool_info.get('output'):
                                st.code(tool_info['output'], language="text")
                            if tool_info.get('error'):
                                st.error(tool_info['error'])

with col2:
    st.header("🔧 即時工具監控")
    
    # 工具狀態監控區域
    tool_status_container = st.container()
    
    with tool_status_container:
        st.subheader("📊 系統狀態")
        st.success("✅ Mem0 記憶系統")
        st.success("✅ 天氣 API")
        st.success("✅ HTTP 請求工具")
        
        st.subheader("👤 當前會話")
        st.info(f"用戶 ID: {USER_ID}")
        st.info(f"對話輪次: {len(st.session_state.messages)}")
        st.info(f"工具調用: {len(st.session_state.tool_calls)}")

# 快速建議按鈕
st.markdown("### 💡 快速開始")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("💕 約會穿搭", use_container_width=True):
        user_input = "我明天要去約會，該穿什麼？"
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

with col2:
    if st.button("💼 上班穿搭", use_container_width=True):
        user_input = "幫我搭配上班服裝"
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

with col3:
    if st.button("🌟 休閒穿搭", use_container_width=True):
        user_input = "我想要週末休閒穿搭建議"
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

with col4:
    if st.button("👤 測試記憶", use_container_width=True):
        user_input = "我是 Johnny，喜歡韓式風格"
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

# 用戶輸入區域
if prompt := st.chat_input("告訴我您的穿搭需求..."):
    # 添加用戶消息到歷史
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 顯示用戶消息
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # 生成並顯示助手回應
    with st.chat_message("assistant", avatar="👗"):
        message_placeholder = st.empty()
        tool_monitoring = st.expander("🔧 即時工具調用監控", expanded=True)
        
        # 顯示思考中的提示
        message_placeholder.markdown("🤔 Strands 正在思考中...")
        
        # 即時工具監控
        with tool_monitoring:
            status_placeholder = st.empty()
            output_placeholder = st.empty()
            
            status_placeholder.info("🔄 正在處理請求...")
            
            try:
                # 捕獲所有輸出
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                
                # 顯示開始調用
                status_placeholder.info("🔄 調用 Strands Agent...")
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    response = outfit_agent(prompt, user_id=USER_ID)
                
                # 獲取工具輸出
                tool_output = stdout_capture.getvalue()
                tool_errors = stderr_capture.getvalue()
                
                # 顯示工具調用結果
                if tool_output:
                    status_placeholder.success("✅ 工具調用完成")
                    output_placeholder.code(tool_output, language="text")
                    
                    # 解析工具調用
                    tool_call_info = {}
                    if "Tool #" in tool_output:
                        lines = tool_output.split('\n')
                        current_tool = None
                        for line in lines:
                            if "Tool #" in line and ":" in line:
                                current_tool = line.split(':')[1].strip()
                                tool_call_info[current_tool] = {"output": "", "error": ""}
                            elif current_tool:
                                tool_call_info[current_tool]["output"] += line + "\n"
                    
                    # 記錄工具調用
                    st.session_state.tool_calls.append(tool_call_info)
                else:
                    status_placeholder.info("ℹ️ 未使用任何工具")
                    st.session_state.tool_calls.append({})
                
                if tool_errors:
                    st.error(f"工具調用錯誤：{tool_errors}")
                
                # 顯示最終回應
                message_placeholder.markdown(response)
                
                # 添加到對話歷史
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                status_placeholder.error(f"❌ 錯誤：{str(e)}")
                error_message = f"抱歉，我暫時無法回應。請稍後再試！😔"
                message_placeholder.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
                st.session_state.tool_calls.append({})

# 側邊欄 - 詳細監控
with st.sidebar:
    st.header("🔧 詳細監控")
    
    # 清除對話按鈕
    if st.button("🗑️ 清除對話", use_container_width=True):
        st.session_state.messages = []
        st.session_state.tool_calls = []
        st.rerun()
    
    st.markdown("---")
    
    # 工具調用歷史
    st.subheader("📋 工具調用歷史")
    
    if st.session_state.tool_calls:
        for i, tool_call in enumerate(st.session_state.tool_calls):
            if tool_call:
                st.markdown(f"**第 {i+1} 次對話：**")
                for tool_name, tool_info in tool_call.items():
                    st.markdown(f"• {tool_name}")
                st.markdown("---")
            else:
                st.markdown(f"**第 {i+1} 次對話：** 未使用工具")
                st.markdown("---")
    else:
        st.info("尚無工具調用記錄")
    
    st.markdown("---")
    
    # 環境信息
    st.subheader("🌍 環境信息")
    st.code(f"""
USER_ID: {USER_ID}
MEM0_API_KEY: {"已設定" if os.environ.get('MEM0_API_KEY') else "未設定"}
WEATHER_API: {"已設定" if OPENWEATHER_API_KEY != 'demo_key' else "未設定"}
    """)

# 頁腳
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; padding: 1rem;">'
    ' Strands Agent | 完整工具調用監控 | '
    ' Ginny Huang - AWS © 2025'
    '</div>', 
    unsafe_allow_html=True
)