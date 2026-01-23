import streamlit as st
import os
import io
import streamlit.components.v1 as components
import requests
import converter

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

# --- Sidebar: File Explorer & Upload ---
with st.sidebar:
    st.title("📂 Explorer")
    
    # 1. Upload File (Best for Online Use)
    uploaded_file = st.file_uploader("Upload a local file", type=['md', 'txt', 'py', 'js', 'json', 'yaml', 'html', 'css'])
    
    st.markdown("---")
    
    # 2. GitHub URL (Great for Remote Files)
    github_url = st.text_input("Enter GitHub URL", placeholder="https://github.com/user/repo/blob/main/README.md")

    st.markdown("---")
    
    # 3. Local File System (Good for Local Use)
    st.subheader("Local Filesystem")
    
    # Navigation controls
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"`{st.session_state.current_path}`")
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
        
        # Directories
        for d in directories:
            if st.button(f"📁 {d}", key=f"dir_{d}"):
                st.session_state.current_path = os.path.join(st.session_state.current_path, d)
                st.rerun()
        
        # Files
        for f in files:
            icon = "📄"
            if f.endswith('.md'): icon_emoji = "📝"
            else: icon_emoji = "📄"
            
            if st.button(f"{icon_emoji} {f}", key=f"file_{f}"):
                st.session_state.selected_file = os.path.join(st.session_state.current_path, f)
                # Clear uploaded file if user selects a local file
                uploaded_file = None 

    except PermissionError:
        st.error("Permission Denied")

# --- Main Area: Preview ---
content = None
filename = ""

# Logic: Uploaded file takes priority, otherwise selected local file
if uploaded_file is not None:
    filename = uploaded_file.name
    try:
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        content = stringio.read()
    except Exception as e:
        st.error(f"Error reading uploaded file: {e}")
elif github_url:
    # Logic to handle GitHub URLs
    if "github.com" in github_url and "/blob/" in github_url:
        # Convert blob URL to raw URL
        raw_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    else:
        raw_url = github_url
    
    filename = os.path.basename(github_url)
    try:
        response = requests.get(raw_url)
        if response.status_code == 200:
            content = response.text
        else:
            st.error(f"Failed to fetch file from GitHub. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error fetching from GitHub: {e}")

elif st.session_state.selected_file:
    file_path = st.session_state.selected_file
    filename = os.path.basename(file_path)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            st.error(f"Error reading file: {e}")
else:
    st.info("👈 Select a file, upload one, or enter a GitHub URL.")
    main_uploaded_file = st.file_uploader("Upload a local file", type=['md', 'txt', 'py', 'js', 'json', 'yaml', 'html', 'css'], key="main_uploader")
    if main_uploaded_file is not None:
        filename = main_uploaded_file.name
        try:
            stringio = io.StringIO(main_uploaded_file.getvalue().decode("utf-8"))
            content = stringio.read()
            uploaded_file = main_uploaded_file # Make it behave like the sidebar uploader for rendering checks
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")

if content is not None:
    st.title(filename)
    if uploaded_file:
         st.caption("Source: Uploaded File")
    elif github_url:
         st.caption(f"Source: GitHub ({github_url})")
    else:
         st.caption(f"Path: {st.session_state.selected_file}")
    
    # --- Print Support ---
    st.markdown("""
        <style>
        @media print {
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="stHeader"] { display: none !important; }
            .stApp > header { display: none !important; }
            button { display: none !important; }
            .block-container { padding-top: 0 !important; }
        }
        </style>
    """, unsafe_allow_html=True)

    # Download Buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        try:
            pdf_file = converter.convert_to_pdf(content)
            st.download_button(
                label="Download PDF",
                data=pdf_file,
                file_name=f"{os.path.splitext(filename)[0]}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF Conversion Failed: {e}")

    with col2:
        try:
            docx_file = converter.convert_to_docx(content)
            st.download_button(
                label="Download DOCX",
                data=docx_file,
                file_name=f"{os.path.splitext(filename)[0]}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
             st.error(f"DOCX Conversion Failed: {e}")
             
    with col3:
        if st.button("🖨️ Print View"):
            components.html("""
            <script>
                try {
                    window.parent.print();
                } catch (e) {
                    console.error("Print failed from iframe", e);
                    alert("Unable to trigger print automatically. Please press Ctrl+P to print.");
                }
            </script>
            """, height=0, width=0)

    st.markdown("---")

    if filename.endswith('.md'):
        parts = content.split("```mermaid")
        
        for i, part in enumerate(parts):
            if i == 0:
                st.markdown(part)
            else:
                subparts = part.split("```", 1)
                if len(subparts) == 2:
                    mermaid_code = subparts[0]
                    remainder = subparts[1]
                    
                    st.write("Graph/Chart:")
                    mermaid(mermaid_code)
                    st.markdown(remainder)
                else:
                    st.markdown("```mermaid" + part)
    else:
        st.code(content)
