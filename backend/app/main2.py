import sys
sys.path.append('/Users/yuyangyang/Documents/Studying/CUHK/9_IS_Practicum/hkia_saka_v2')
import streamlit as st
from backend.app.llm.rag_query import rag_query


# Set fixed username and password
USERNAME = "admin"
PASSWORD = "hkia2025"

# Initialize login status
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_page():
    """Display login page and handle authentication"""
    st.title("🔐 Login")
    
    # Create login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username == USERNAME and password == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect username or password, please try again!")

def main_app():
    """Display main application content - only shown after login"""
    st.title(" 🛩️ SAKA")
    st.caption("👩🏻‍💼 Your Smart AI Airport Operation Assistant.")

    with st.sidebar:
        st.header("⚙️ Configuration")
        selected_model = st.selectbox(
            "Choose Model",
            ["deepseek-r1:1.5b", "deepseek-r1:3b"],
            index=0
        )
        st.divider()
        st.markdown("### SAKA Capabilities")
        st.markdown("""
            - Provide step-by-step advice based on airport manuals
            - Answer questions about airport operations
            - Guide through emergency procedures
        """)
        st.divider()
        
        # Add logout button
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    # Session state management
    if "message_log" not in st.session_state:
        st.session_state.message_log = [{
            "role": "assistant", 
            "content": "Hi! I'm SAKA. How can I help you with airport operations today?",
            "image_paths": []
        }]

    # Chat container
    chat_container = st.container()

    # Display chat messages
    with chat_container:
        for message in st.session_state.message_log:
            with st.chat_message(message["role"]):
                # 显示文本内容
                st.markdown(message["content"])
                
                # 如果是助手回复且包含图片，显示图片
                if message["role"] == "assistant" and "image_paths" in message and message["image_paths"]:
                    st.markdown("**References：**")
                    img_cols = st.columns(min(len(message["image_paths"]), 3))
                    for i, img_path in enumerate(message["image_paths"]):
                        try:
                            with img_cols[i % 3]:
                                st.image(img_path, caption=f"Image {i+1}", use_container_width=True)
                        except Exception as img_err:
                            pass  # 静默处理历史图片加载错误

    # User input
    if prompt := st.chat_input("Please enter your question..."):
        # Add user message to history
        st.session_state.message_log.append({
            "role": "user", 
            "content": prompt,
            "image_paths": []
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant message
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Process response
            try:
                # 获取流式响应和图片路径列表
                streamer, image_paths = rag_query(prompt)

                # 流式输出文本
                for new_text in streamer:
                    full_response += new_text
                    message_placeholder.markdown(full_response + "▌")

                # 显示完整回答
                message_placeholder.markdown(full_response)
                
                # 在同一个聊天气泡内显示图片
                if image_paths:
                    st.divider()
                    st.markdown("**References：**")
                    cols = st.columns(min(len(image_paths), 3))
                    for i, img_path in enumerate(image_paths):
                        try:
                            with cols[i % 3]:
                                st.image(img_path, caption=f"Image {i+1}", use_container_width=True)
                        except Exception as img_err:
                            st.error(f"无法加载图片: {img_path}. 错误: {str(img_err)}")

                # 保存回复到历史记录，包含文本和图片路径
                st.session_state.message_log.append({
                    "role": "assistant", 
                    "content": full_response,
                    "image_paths": image_paths if image_paths else []
                })

            except Exception as e:
                st.error(f"模型加载或生成错误: {str(e)}")
                # 添加空消息避免错误状态
                st.session_state.message_log.append({
                    "role": "assistant",
                    "content": "抱歉，处理您的请求时遇到了问题。",
                    "image_paths": []
                })

# Display login page or main app based on authentication status
if not st.session_state.authenticated:
    login_page()
else:
    main_app()