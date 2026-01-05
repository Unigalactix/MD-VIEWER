import streamlit as st
import os
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Markdown Viewer")

# --- Mermaid implementation ---
def mermaid(code: str, height=500):
    html_code = f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
        
        function downloadSVG() {{
            const svg = document.querySelector('.mermaid svg');
            if (svg) {{
                const data = (new XMLSerializer()).serializeToString(svg);
                const blob = new Blob([data], {{type: 'image/svg+xml;charset=utf-8'}});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'diagram.svg';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }}
        }}
    </script>
    <div style="position: relative;">
        <button onclick="downloadSVG()" style="position: absolute; top: 0; right: 0; z-index: 10; opacity: 0.7; cursor: pointer; background: #333; color: white; border: none; padding: 5px 10px; border-radius: 4px; font-size: 12px;">⬇️ SVG</button>
        <div class="mermaid">
        {code}
        </div>
    </div>
    """
    return components.html(html_code, height=height, scrolling=True)

# --- State Management ---
if 'current_path' not in st.session_state:
    st.session_state.current_path = os.getcwd()

if 'selected_file' not in st.session_state:
    st.session_state.selected_file = None

# --- Sidebar: File Explorer ---
with st.sidebar:
    st.title("📂 Explorer")
    
    # Navigation controls
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"**Path:** `{st.session_state.current_path}`")
    with col2:
        if st.button("⬆️"):
            st.session_state.current_path = os.path.dirname(st.session_state.current_path)
            st.rerun()

    # List items
    try:
        items = os.listdir(st.session_state.current_path)
        directories = [d for d in items if os.path.isdir(os.path.join(st.session_state.current_path, d))]
        files = [f for f in items if os.path.isfile(os.path.join(st.session_state.current_path, f))]
        
        directories.sort()
        files.sort()

        st.markdown("---")
        
        # Directories
        for d in directories:
            if st.button(f"📁 {d}", key=f"dir_{d}"):
                st.session_state.current_path = os.path.join(st.session_state.current_path, d)
                st.rerun()
        
        # Files
        for f in files:
            icon = "📄"
            if f.endswith('.md'): icon = "markdown" # Visual indicator only
            if f.endswith('.md'): icon_emoji = "📝"
            else: icon_emoji = "📄"
            
            if st.button(f"{icon_emoji} {f}", key=f"file_{f}"):
                st.session_state.selected_file = os.path.join(st.session_state.current_path, f)

    except PermissionError:
        st.error("Permission Denied")

# --- Main Area: Preview ---
if st.session_state.selected_file:
    file_path = st.session_state.selected_file
    filename = os.path.basename(file_path)
    
    st.title(filename)
    st.caption(f"Path: {file_path}")
    st.markdown("---")

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if filename.endswith('.md'):
                # Custom rendering to intercept mermaid blocks could be complex.
                # Simplest way: Split by mermaid blocks or just instruct user.
                # For this demo, we'll try to find mermaid blocks and render them separately if possible,
                # but standard st.markdown doesn't support it.
                # Let's do a simple split if "```mermaid" exists
                
                parts = content.split("```mermaid")
                
                for i, part in enumerate(parts):
                    if i == 0:
                        st.markdown(part)
                    else:
                        # part starts with mermaid code, ends with ``` usually
                        # Find the closing ```
                        subparts = part.split("```", 1)
                        if len(subparts) == 2:
                            mermaid_code = subparts[0]
                            remainder = subparts[1]
                            
                            st.write("Graph/Chart:")
                            mermaid(mermaid_code)
                            st.markdown(remainder)
                        else:
                            # Fallback
                            st.markdown("```mermaid" + part)
                            
            else:
                st.code(content)
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.error("File not found.")
else:
    st.info("Select a file from the sidebar to view.")
