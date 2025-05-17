import sys
sys.path.append('/Users/yuyangyang/Documents/Studying/CUHK/9_IS_Practicum/hkia_saka_v2')
import streamlit as st
from backend.app.llm.rag_query import rag_query
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

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

def stats_page():
    """Display statistics about document retrieval"""
    st.title("📊 Retrieval Analytics")
    
    # Connect to database
    try:
        conn = sqlite3.connect('backend/data/logs/query_logs.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='doc_logs'")
        if not cursor.fetchone():
            st.info("No query logs found. Start asking questions to generate data.")
            return
        
        # Time period selection
        st.sidebar.header("Filter Options")
        days_option = st.sidebar.selectbox(
            "Time Period",
            ["Today", "Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
            index=0
        )
        
        # Build time filter condition
        if days_option == "All Time":
            time_condition = ""
            time_message = "All Time"
        elif days_option == "Today":
            today = datetime.now().strftime("%Y-%m-%d")
            time_condition = f"DATE(timestamp) = '{today}'"
            time_message = "Today"
        else:
            # Extract number of days from the option
            days = int(days_option.split()[1])
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            time_condition = f"timestamp > '{cutoff_date}'"
            time_message = f"{days_option}"
            
        # Display header with time period
        st.header(f"Retrieval Statistics ({time_message})")
        
        # Top manuals retrieved
        st.subheader("Most Referenced Manuals")
        if time_condition:
            query = f"""
                SELECT source_manual, COUNT(*) as count 
                FROM doc_logs 
                WHERE {time_condition}
                GROUP BY source_manual 
                ORDER BY count DESC 
                LIMIT 3
            """
        else:
            query = """
                SELECT source_manual, COUNT(*) as count 
                FROM doc_logs 
                GROUP BY source_manual 
                ORDER BY count DESC 
                LIMIT 3
            """
        df_manuals = pd.read_sql(query, conn)
        
        if not df_manuals.empty and df_manuals['count'].sum() > 0:
            fig = px.bar(
                df_manuals, 
                x='source_manual', 
                y='count', 
                labels={'source_manual': 'Manual', 'count': 'References'},
                title="Top Referenced Manuals"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No manual references found in the selected time period.")
        
        # Top Header1 sections retrieved
        st.subheader("Most Referenced Primary Sections")
        if time_condition:
            query = f"""
                SELECT Header1, COUNT(*) as count 
                FROM doc_logs 
                WHERE {time_condition} AND Header1 IS NOT NULL AND Header1 != ''
                GROUP BY Header1 
                ORDER BY count DESC 
                LIMIT 10
            """
        else:
            query = """
                SELECT Header1, COUNT(*) as count 
                FROM doc_logs 
                WHERE Header1 IS NOT NULL AND Header1 != ''
                GROUP BY Header1 
                ORDER BY count DESC 
                LIMIT 10
            """
        df_header1 = pd.read_sql(query, conn)
        
        if not df_header1.empty and df_header1['count'].sum() > 0:
            fig = px.bar(
                df_header1, 
                x='Header1', 
                y='count', 
                labels={'Header1': 'Primary Section', 'count': 'References'},
                title="Top 10 Referenced Primary Sections"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No primary section references found in the selected time period.")
        
        # Top Header2 subsections retrieved
        st.subheader("Most Referenced Subsections")
        if time_condition:
            query = f"""
                SELECT Header2, COUNT(*) as count 
                FROM doc_logs 
                WHERE {time_condition} AND Header2 IS NOT NULL AND Header2 != ''
                GROUP BY Header2 
                ORDER BY count DESC 
                LIMIT 10
            """
        else:
            query = """
                SELECT Header2, COUNT(*) as count 
                FROM doc_logs 
                WHERE Header2 IS NOT NULL AND Header2 != ''
                GROUP BY Header2 
                ORDER BY count DESC 
                LIMIT 10
            """
        df_header2 = pd.read_sql(query, conn)
        
        if not df_header2.empty and df_header2['count'].sum() > 0:
            fig = px.bar(
                df_header2, 
                x='Header2', 
                y='count', 
                labels={'Header2': 'Subsection', 'count': 'References'},
                title="Top 10 Referenced Subsections"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No subsection references found in the selected time period.")
        
        # Document type distribution
        st.subheader("Document Type Distribution")
        if time_condition:
            query = f"""
                SELECT type, COUNT(*) as count 
                FROM doc_logs 
                WHERE {time_condition}
                GROUP BY type
            """
        else:
            query = """
                SELECT type, COUNT(*) as count 
                FROM doc_logs 
                GROUP BY type
            """
        df_types = pd.read_sql(query, conn)
        
        if not df_types.empty and df_types['count'].sum() > 0:
            fig = px.pie(
                df_types, 
                values='count', 
                names='type', 
                title="Document Types Retrieved",
                color_discrete_map={'text': '#3366CC', 'image': '#FF9900'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No document type data found in the selected time period.")
            
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def chat_page():
    """Display the main chat interface"""
    st.title(" 🛩️ SAKA")
    st.caption("👩🏻‍💼 Your Smart AI Airport Operation Assistant.")
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        selected_mode = st.radio(
            "Choose Answer Mode",
            ["Straightforward", "Comprehensive"],
            index=0
        )
        st.divider()
        st.markdown("### Guidance")
        st.markdown("""
            - In **Configuration**, you can select the **Answer Mode**:
                - **Straightforward**: Offers concise, step-by-step answers for simple queries.
                - **Comprehensive**: Delivers in-depth, detailed responses suited for analytical or complex issues.

                    
            - In **Navigation**, choose **Analytics Dashboard** to access statistical insights, including the most frequently queried manual topics.
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
            "content": "Hi! I'm SAKA. How can I help you today?",
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
                streamer, top_docs = rag_query(prompt, selected_mode)

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

def main_app():
    """Display main application with navigation"""
    # Add sidebar navigation
    with st.sidebar:
        st.title("🏠 Navigation")
        page = st.radio("Go to", ["Chat Assistant", "Analytics Dashboard"])
    
    # Display selected page
    if page == "Chat Assistant":
        chat_page()
    else:
        stats_page()

# Display login page or main app based on authentication status
if not st.session_state.authenticated:
    login_page()
else:
    main_app()