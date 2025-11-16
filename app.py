import streamlit as st
import sqlite3

DB_NAME = "todos.db"

# Database functions
def db_execute(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(query, params)
    result = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return result

def init_db():
    db_execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

def add_task(task):
    db_execute("INSERT INTO tasks (task) VALUES (?)", (task,))

def get_tasks():
    return db_execute("SELECT id, task, completed, created_at FROM tasks ORDER BY created_at DESC", fetch=True)

def toggle_task(task_id):
    db_execute("UPDATE tasks SET completed = NOT completed WHERE id = ?", (task_id,))

def delete_task(task_id):
    db_execute("DELETE FROM tasks WHERE id = ?", (task_id,))

def delete_completed():
    db_execute("DELETE FROM tasks WHERE completed = 1")

# Initialize
init_db()
st.set_page_config(page_title="To-Do List App", page_icon="✅", layout="centered")

# Blue theme CSS
st.markdown("""<style>
.stApp {background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);}
.stMarkdown, .stText, p, span, label {color: #FFFFFF !important;}
h1, h2, h3 {color: #FFFFFF !important;}
.stTextInput input {background-color: #2a5298 !important; color: #FFFFFF !important; border: 1px solid #4A90E2 !important;}
.stButton button {background-color: #FF4B4B !important; color: white !important; border: none !important;}
.stButton button:hover {background-color: #FF6B6B !important;}
.stFormSubmitButton button {background-color: #00CC66 !important; color: white !important;}
.stFormSubmitButton button:hover {background-color: #00DD77 !important;}
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {color: #FFFFFF !important;}
.stRadio label, .stCheckbox label {color: #FFFFFF !important;}
.stAlert {background-color: rgba(42, 82, 152, 0.7) !important; color: #FFFFFF !important;}
hr {border-color: #4A90E2 !important;}
</style>""", unsafe_allow_html=True)

st.title("✅ To-Do List App")
st.markdown("---")

# Add task
st.subheader("➕ Add New Task")
with st.form("add_task_form", clear_on_submit=True):
    new_task = st.text_input("Enter a new task:", placeholder="e.g., Buy groceries")
    if st.form_submit_button("Add Task"):
        if new_task.strip():
            add_task(new_task.strip())
            st.success(f"✓ Added: {new_task}")
            st.rerun()
        else:
            st.warning("Please enter a task!")

st.markdown("---")

# Display tasks
st.subheader("📋 Your Tasks")
tasks = get_tasks()

if not tasks:
    st.info("No tasks yet! Add one above to get started.")
else:
    # Stats
    total, completed = len(tasks), sum(1 for t in tasks if t[2])
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tasks", total)
    col2.metric("Completed", completed)
    col3.metric("Pending", total - completed)
    
    st.markdown("---")
    
    # Filter
    filter_opt = st.radio("Filter tasks:", ["All", "Pending", "Completed"], horizontal=True)
    filtered = [t for t in tasks if filter_opt == "All" or 
                (filter_opt == "Pending" and not t[2]) or 
                (filter_opt == "Completed" and t[2])]
    
    if not filtered:
        st.info(f"No {filter_opt.lower()} tasks.")
    else:
        for task_id, task_text, is_completed, _ in filtered:
            col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
            
            with col1:
                if st.checkbox("", value=bool(is_completed), key=f"c_{task_id}") != bool(is_completed):
                    toggle_task(task_id)
                    st.rerun()
            
            with col2:
                st.markdown(f"~~{task_text}~~" if is_completed else task_text)
            
            with col3:
                if st.button("🗑️", key=f"d_{task_id}"):
                    delete_task(task_id)
                    st.rerun()
            
            st.markdown("---")
    
    # Bulk delete
    if completed > 0 and st.button("🧹 Clear All Completed Tasks"):
        delete_completed()
        st.success("Cleared all completed tasks!")
        st.rerun()

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Built with Streamlit | Data stored in SQLite</div>", unsafe_allow_html=True)