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
            "references": [],
            "image_paths": []
        }]

    # Chat container
    chat_container = st.container()

    # Display chat messages
    with chat_container:
        for message in st.session_state.message_log:
            with st.chat_message(message["role"]):
                # Display text content
                st.markdown(message["content"])
                
                # If it's an assistant reply with references or images, display reference materials
                if message["role"] == "assistant":
                    # Display text references
                    if "references" in message and message["references"]:
                        st.divider()
                        st.markdown("**References：**")
                        for i, ref in enumerate(message["references"]):
                            st.markdown(f"{i+1}. {ref}")
                    
                    # Display images
                    if "image_paths" in message and message["image_paths"]:
                        # If no text references but has images
                        if not message.get("references") and message["image_paths"]:
                            st.divider()
                            st.markdown("**References：**")
                        
                        img_cols = st.columns(min(len(message["image_paths"]), 3))
                        for i, img_path in enumerate(message["image_paths"]):
                            try:
                                with img_cols[i % 3]:
                                    st.image(img_path, caption=f"Image {i+1}", use_container_width=True)
                            except Exception as img_err:
                                pass  # Silently handle historical image loading errors

    # User input
    if prompt := st.chat_input("Please enter your question..."):
        # Add user message to history
        st.session_state.message_log.append({
            "role": "user", 
            "content": prompt,
            "references": [],
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
                # Get streaming response and document list
                streamer, top_docs = rag_query(prompt)

                # Stream output text
                for new_text in streamer:
                    full_response += new_text
                    message_placeholder.markdown(full_response + "▌")

                # Display complete answer
                message_placeholder.markdown(full_response)
                
                # Extract reference materials and image paths
                references = []
                image_paths = []
                
                for doc in top_docs:
                    # Extract reference info (for all document types)
                    source = doc.metadata.get('source_manual', '').strip()
                    header1 = doc.metadata.get('Header1', '').strip()
                    header2 = doc.metadata.get('Header2', '').strip()
                    
                    # Build reference info string
                    ref_info = f"{source}"
                    if header1:
                        ref_info += f" - {header1}"
                    if header2:
                        ref_info += f" - {header2}"
                    if ref_info not in references:    
                        references.append(ref_info)
                    
                    # Check if it's an image type
                    if doc.metadata.get('type') == 'image' and 'image_path' in doc.metadata:
                        image_paths.append(doc.metadata['image_path'])
                
                # Display reference info within the same chat bubble
                if references or image_paths:
                    st.divider()
                    st.markdown("**References：**")
                    
                    # Display text reference info
                    for i, ref in enumerate(references):
                        st.markdown(f"{i+1}. {ref}")
                
                # Display images (if any)
                if image_paths:
                    cols = st.columns(min(len(image_paths), 3))
                    for i, img_path in enumerate(image_paths):
                        try:
                            with cols[i % 3]:
                                st.image(img_path, caption=f"Image {i+1}", use_container_width=True)
                        except Exception as img_err:
                            st.error(f"Unable to load image: {img_path}. Error: {str(img_err)}")

                # Save response and reference info to history
                st.session_state.message_log.append({
                    "role": "assistant", 
                    "content": full_response,
                    "references": references,
                    "image_paths": image_paths
                })

            except Exception as e:
                st.error(f"Model loading or generation error: {str(e)}")
                # Add empty message to avoid error state
                st.session_state.message_log.append({
                    "role": "assistant",
                    "content": f"Sorry, there was a problem processing your request: {str(e)}",
                    "references": [],
                    "image_paths": []
                })

# Display login page or main app based on authentication status
if not st.session_state.authenticated:
    login_page()
else:
    main_app()