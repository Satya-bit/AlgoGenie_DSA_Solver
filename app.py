import streamlit as st
from team.dsa_team import get_dsa_team_and_docker
from config.docker_utils import start_docker_container, stop_docker_container
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult
import asyncio

# ---------------- Page & Global Styles -----------------
st.set_page_config(
        page_title="AlgoGenie DSA Solver",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
/* Page background gradient */
.stApp {
    background: radial-gradient(circle at 20% 20%, #1e3c72 0%, #2a5298 35%, #0f2027 100%);
    background-attachment: fixed;
    color: #eef3fa;
    font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

/* Subtle animated gradient overlay */
/* Removed animated overlay effect */

/* Glass card */
.glass-card {
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(12px) saturate(160%);
    -webkit-backdrop-filter: blur(12px) saturate(160%);
    border: 1px solid rgba(255,255,255,0.15);
    padding: 1.2rem 1.4rem;
    border-radius: 18px;
    box-shadow: 0 8px 24px -6px rgba(0,0,0,0.45);
    margin-bottom: 1.2rem;
}

/* Title styling */
.main-title {font-size:3rem; font-weight:700; letter-spacing:1px; background: linear-gradient(90deg,#66d1ff,#ffb347,#ff6b6b); -webkit-background-clip:text; color:transparent; text-align:center; margin: 0 0 0.4rem 0;}
.subtitle {text-align:center; font-size:1.1rem; color:#c7d6e6; margin-bottom:1.8rem;}

/* Chat message styles */
.msg-block {padding:0.75rem 1rem; border-radius:14px; margin-bottom:0.6rem; line-height:1.35; font-size:0.95rem; box-shadow:0 4px 12px -4px rgba(0,0,0,0.5);} 
.role-user {background:linear-gradient(135deg,#4e9af1,#3778c2); border:1px solid rgba(255,255,255,0.25);} 
.role-agent {background:linear-gradient(135deg,#6a5af9,#8369ff); border:1px solid rgba(255,255,255,0.25);} 
.role-exec {background:linear-gradient(135deg,#11998e,#38ef7d); border:1px solid rgba(255,255,255,0.25);} 
.role-stop {background:linear-gradient(135deg,#ff512f,#dd2476); border:1px solid rgba(255,255,255,0.25);} 
.role-error {background:linear-gradient(135deg,#f00000,#dc281e); border:1px solid rgba(255,255,255,0.25);} 

.msg-block b {font-weight:600; display:block; margin-bottom:0.2rem; letter-spacing:0.5px;}

/* Text area */
textarea {border-radius:14px !important; border:1px solid #3d5a80 !important;}

/* Run button */
+div.stButton > button:first-child {
+  background: linear-gradient(90deg,#ffe7a0,#ffca5f) !important;
+  color:#000 !important; font-weight:700; letter-spacing:0.6px; border:0; border-radius:14px; padding:0.75rem 1.2rem; box-shadow:0 6px 18px -4px rgba(0,0,0,0.55);
+  text-shadow:none !important;
+}
+div.stButton > button:first-child:hover {filter:brightness(1.05) saturate(1.15); box-shadow:0 8px 22px -6px rgba(0,0,0,0.65);} 

/* Sidebar */
section[data-testid="stSidebar"] {background: linear-gradient(180deg,#0f2027,#203a43,#2c5364); border-right:1px solid rgba(255,255,255,0.1);} 
section[data-testid="stSidebar"] * {color:#e2ecf5 !important;}

/* Footer hide */
footer {visibility:hidden; height:0;}

</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------- Sidebar Content -----------------
with st.sidebar:
        st.markdown("""### 🔍 Tips
* Be specific in your problem.
* Mention constraints if known.

### 🧰 Features
* Multi-agent reasoning
* Code execution in Docker
* Streaming responses
""")
        st.divider()
        st.markdown("Made using *Streamlit* & *Autogen*.")

# ---------------- Header -----------------
st.markdown("""
<div class="glass-card">
        <div class="main-title">AlgoGenie DSA Solver</div>
        <div class="subtitle">Interactive AI agents that help you reason, explain & execute DSA problems.</div>
</div>
""", unsafe_allow_html=True)

# ---------------- Input Form -----------------
with st.form("dsa_input_form", clear_on_submit=False):
        task = st.text_area(
                "📝 Enter your DSA problem statement:",
                value='Write a function to add two numbers',
                height=140,
                placeholder="E.g., Given a binary tree, return its level-order traversal..."
        )
        submitted = st.form_submit_button("🚀 Run Solution")

async def run(team,docker, task):
    try:
        await start_docker_container(docker)
        async for message in team.run_stream(task=task):
            if isinstance(message, TextMessage):
                print(msg:= f"{message.source}: {message.content}")
                yield msg
            elif isinstance(message, TaskResult):
                print(msg:= f"Stop Reason: {message.stop_reason}")
                yield msg
        print("Task completed")

    except Exception as e:
        print(f"Error:{e}")
        yield f"Error:{e}"
    finally:
        await stop_docker_container(docker)

if submitted:
    if not task.strip():
        st.warning("Please enter a problem first.")
    else:
        st.markdown('<div class="glass-card" style="border:1px solid #3d5a80;">⚙️ <b>Initializing agents & Docker...</b></div>', unsafe_allow_html=True)
        output_container = st.container()

        team,docker=get_dsa_team_and_docker()

        def render_message(raw: str):
            if raw.startswith("user"):
                css_class = "role-user"; label = "🧑 User"
            elif raw.startswith("DSA_Problem_Solver_Agent"):
                css_class = "role-agent"; label = "💻 Solver Agent"
            elif raw.startswith("CodeExecutorAgent"):
                css_class = "role-exec"; label = "🤖 Code Executor"
            elif raw.startswith("Error:"):
                css_class = "role-error"; label = "⛔ Error"
            else:
                css_class = "role-agent"; label = "💬 Message"
            # Escape nothing for now (assuming safe origins) – could add html.escape if needed
            return f'<div class="msg-block {css_class}"><b>{label}</b>{raw}</div>'

        async def collect_messages():
            async for msg in run(team,docker,task):
                if isinstance(msg,str):
                    with output_container:
                        st.markdown(render_message(msg), unsafe_allow_html=True)
                elif isinstance(msg,TaskResult):
                    with output_container:
                        st.markdown(f'<div class="msg-block role-stop"><b>🛑 Finished</b>Stop Reason: {msg.stop_reason}</div>', unsafe_allow_html=True)

        asyncio.run(collect_messages())
    
          
    
    