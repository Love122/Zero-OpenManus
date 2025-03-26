import streamlit as st
import asyncio
from app.agent.manus import Manus
from app.logger import logger
import tomli
import tomli_w
import os

# 设置页面配置
st.set_page_config(
    page_title="OpenManus Web Interface",
    page_icon="🤖",
    layout="wide"
)

# 添加标题和描述
st.title("🤖 OpenManus AI Assistant")
st.markdown("""
这是一个基于OpenManus的AI助手界面，可以帮助你完成各种任务，包括：
- 网页浏览和搜索
- 文件操作
- Python代码执行
- 信息检索
""")

# 创建会话状态
if 'agent' not in st.session_state:
    st.session_state.agent = Manus()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 读取配置文件
def load_config():
    with open("config/config.toml", "rb") as f:
        return tomli.load(f)

def save_config(config):
    with open("config/config.toml", "wb") as f:
        tomli_w.dump(config, f)

# 创建侧边栏配置
with st.sidebar:
    st.header("配置")

    # LLM配置
    with st.expander("LLM配置", expanded=False):
        config = load_config()
        llm_config = config.get("llm", {})

        llm_model = st.text_input("LLM Model", value=llm_config.get("model", ""))
        llm_base_url = st.text_input("LLM Base URL", value=llm_config.get("base_url", ""))
        llm_api_key = st.text_input("LLM API Key", value=llm_config.get("api_key", ""), type="password")
        llm_max_tokens = st.number_input("LLM Max Tokens", value=llm_config.get("max_tokens", 8192))
        llm_temperature = st.number_input("LLM Temperature", value=llm_config.get("temperature", 0.0), min_value=0.0, max_value=1.0, step=0.1)

    # Vision配置
    with st.expander("Vision配置", expanded=False):
        vision_config = config.get("llm", {}).get("vision", {})

        vision_model = st.text_input("Vision Model", value=vision_config.get("model", ""))
        vision_base_url = st.text_input("Vision Base URL", value=vision_config.get("base_url", ""))
        vision_api_key = st.text_input("Vision API Key", value=vision_config.get("api_key", ""), type="password")
        vision_max_tokens = st.number_input("Vision Max Tokens", value=vision_config.get("max_tokens", 8192))
        vision_temperature = st.number_input("Vision Temperature", value=vision_config.get("temperature", 0.0), min_value=0.0, max_value=1.0, step=0.1)

    # 保存配置按钮
    if st.button("保存配置"):
        config["llm"] = {
            "model": llm_model,
            "base_url": llm_base_url,
            "api_key": llm_api_key,
            "max_tokens": llm_max_tokens,
            "temperature": llm_temperature,
        }
        config["llm"]["vision"] = {
            "model": vision_model,
            "base_url": vision_base_url,
            "api_key": vision_api_key,
            "max_tokens": vision_max_tokens,
            "temperature": vision_temperature
        }
        save_config(config)
        st.success("配置已保存！")

    st.markdown("---")
    st.markdown("### 浏览器设置")
    headless = st.checkbox("无头模式", value=False)
    disable_security = st.checkbox("禁用安全特性", value=True)

    st.markdown("---")
    st.markdown("### 搜索引擎设置")
    search_engine = st.selectbox(
        "选择搜索引擎",
        ["Google", "Baidu", "DuckDuckGo"],
        index=0
    )

# 创建主界面
st.markdown("---")
st.subheader("对话历史")

# 显示聊天历史
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("输入你的问题..."):
    # 添加用户消息到历史
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 显示助手响应
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                # 运行AI代理
                asyncio.run(st.session_state.agent.run(prompt))
                st.success("任务完成！")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")
                logger.error(f"Error: {str(e)}")

# 添加清除按钮
if st.button("清除对话历史"):
    st.session_state.chat_history = []
    st.rerun()

# 添加页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Powered by OpenManus | <a href='https://github.com/mannaandpoem/OpenManus'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)
