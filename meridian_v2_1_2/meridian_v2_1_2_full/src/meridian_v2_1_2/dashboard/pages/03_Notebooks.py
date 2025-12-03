"""
Advanced Jupyter Notebook Viewer for Meridian Dashboard

Features:
- Card grid layout with metadata
- Search and tag filtering
- AI-powered summaries
- Smart JupyterLab integration
- Beautiful notebook rendering
"""

import streamlit as st
from pathlib import Path
import os
from datetime import datetime
import socket
import subprocess

try:
    import nbformat
    from nbconvert import HTMLExporter
    NBCONVERT_AVAILABLE = True
except ImportError:
    NBCONVERT_AVAILABLE = False

try:
    import humanize
    HUMANIZE_AVAILABLE = True
except ImportError:
    HUMANIZE_AVAILABLE = False

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
JUPYTER_PORT = 8888

# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def generate_tags(notebook_name):
    """Auto-generate tags based on notebook name"""
    tags = []
    name_lower = notebook_name.lower()
    
    if "backtest" in name_lower:
        tags.append("Backtester")
    if "fld" in name_lower:
        tags.append("FLD")
    if "analysis" in name_lower or "demo" in name_lower:
        tags.append("Analysis")
    if "sweep" in name_lower or "param" in name_lower:
        tags.append("Optimization")
    if "risk" in name_lower:
        tags.append("Risk")
    if "tdom" in name_lower or "seasonal" in name_lower:
        tags.append("Seasonality")
    if "cot" in name_lower:
        tags.append("COT")
    if "cycle" in name_lower:
        tags.append("Cycles")
    if "regime" in name_lower:
        tags.append("Regime")
    
    if not tags:
        tags.append("Notebook")
    
    return tags


def generate_summary(nb):
    """Generate AI-style summary of notebook content"""
    md_cells = [c for c in nb.cells if c.cell_type == "markdown"]
    code_cells = [c for c in nb.cells if c.cell_type == "code"]
    
    # Extract headings
    headings = []
    for cell in md_cells:
        lines = cell.source.split('\n')
        for line in lines:
            if line.strip().startswith('#'):
                headings.append(line.strip())
    
    # Get first markdown cell content (often description)
    first_desc = ""
    if md_cells:
        first_desc = md_cells[0].source[:200].strip()
    
    # Build summary
    summary = f"""
### 📊 Notebook Analysis

**Structure:**
- **Total Cells:** {len(nb.cells)}
- **Markdown Cells:** {len(md_cells)} (documentation)
- **Code Cells:** {len(code_cells)} (executable)

**Table of Contents:**
"""
    
    if headings:
        for i, heading in enumerate(headings[:7]):
            indent = "  " * (heading.count('#') - 1)
            clean_heading = heading.replace('#', '').strip()
            summary += f"\n{indent}- {clean_heading}"
    else:
        summary += "\n- *(No headings found)*"
    
    summary += f"""

**Auto-Generated Summary:**

This notebook contains {len(code_cells)} executable code cells and {len(md_cells)} documentation cells. """
    
    if headings:
        top_topics = [h.replace('#', '').strip() for h in headings[:3]]
        summary += f"The primary focus areas appear to be: **{', '.join(top_topics)}**. "
    
    if first_desc:
        summary += f"\n\n**Introduction:**\n> {first_desc}..."
    
    # Analyze code complexity
    total_lines = sum(len(c.source.split('\n')) for c in code_cells)
    avg_lines = total_lines / len(code_cells) if code_cells else 0
    
    summary += f"""

**Code Complexity:**
- **Total Lines of Code:** ~{total_lines}
- **Average Lines per Cell:** ~{avg_lines:.1f}
- **Complexity Level:** {'High' if avg_lines > 15 else 'Medium' if avg_lines > 7 else 'Low'}
"""
    
    return summary


# ═══════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Meridian - Advanced Notebooks",
    page_icon="📓",
    layout="wide"
)

# Header
st.title("📓 Advanced Jupyter Notebook Viewer")
st.markdown("*Explore, analyze, and interact with research notebooks*")
st.markdown("---")

# Check dependencies
if not NBCONVERT_AVAILABLE:
    st.error("❌ **Missing Dependencies**")
    st.warning("Please install required packages:")
    st.code("pip install nbconvert nbformat jupyter jupyterlab humanize", language="bash")
    st.info("After installation, restart the dashboard.")
    st.stop()

if not HUMANIZE_AVAILABLE:
    st.warning("⚠️ `humanize` package not installed. Install for better date formatting.")

# Check notebooks directory
if not NOTEBOOKS_DIR.exists():
    st.warning(f"📁 Notebooks directory not found: `{NOTEBOOKS_DIR}`")
    if st.button("Create notebooks/ directory"):
        NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
        (NOTEBOOKS_DIR / ".gitkeep").touch()
        st.success("✅ Created notebooks/ directory!")
        st.rerun()
    st.stop()

# Get all notebooks
all_notebooks = sorted(NOTEBOOKS_DIR.glob("*.ipynb"))

if not all_notebooks:
    st.info("📭 No notebooks found in the notebooks/ directory.")
    st.markdown(f"""
**Add notebooks to get started:**
- Place `.ipynb` files in: `{NOTEBOOKS_DIR.relative_to(PROJECT_ROOT)}`
- Supported types:
    - Backtest analysis
    - Strategy research
    - FLD analysis
    - Parameter sweeps
    - Risk studies
""")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Launch JupyterLab"):
            if is_port_in_use(JUPYTER_PORT):
                st.info(f"✅ JupyterLab already running at http://localhost:{JUPYTER_PORT}")
            else:
                try:
                    subprocess.Popen(["jupyter-lab"], cwd=str(PROJECT_ROOT))
                    st.success(f"✅ JupyterLab started at http://localhost:{JUPYTER_PORT}")
                except FileNotFoundError:
                    st.error("❌ JupyterLab not found. Install with: `pip install jupyterlab`")
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# SEARCH & FILTER BAR
# ═══════════════════════════════════════════════════════════════════

st.subheader("🔍 Search & Filter")

col1, col2, col3 = st.columns([3, 2, 1])

with col1:
    search_query = st.text_input(
        "Search notebooks",
        placeholder="Type to search by name...",
        label_visibility="collapsed"
    )

with col2:
    # Get all unique tags
    all_tags = set()
    for nb_path in all_notebooks:
        all_tags.update(generate_tags(nb_path.name))
    
    selected_tags = st.multiselect(
        "Filter by tags",
        sorted(all_tags),
        default=[],
        label_visibility="collapsed"
    )

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("---")

# Filter notebooks based on search and tags
filtered_notebooks = []
for nb_path in all_notebooks:
    # Search filter
    if search_query and search_query.lower() not in nb_path.name.lower():
        continue
    
    # Tag filter
    if selected_tags:
        nb_tags = generate_tags(nb_path.name)
        if not any(tag in nb_tags for tag in selected_tags):
            continue
    
    filtered_notebooks.append(nb_path)

# Display metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Notebooks", len(all_notebooks))
with col2:
    st.metric("Filtered Results", len(filtered_notebooks))
with col3:
    total_size = sum(nb.stat().st_size for nb in all_notebooks) / (1024 * 1024)
    st.metric("Total Size", f"{total_size:.1f} MB")
with col4:
    jupyter_status = "🟢 Running" if is_port_in_use(JUPYTER_PORT) else "⚪ Stopped"
    st.metric("JupyterLab", jupyter_status)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# NOTEBOOK CARD GRID
# ═══════════════════════════════════════════════════════════════════

if not filtered_notebooks:
    st.warning("🔍 No notebooks match your search criteria.")
    st.stop()

st.subheader(f"📚 Notebooks ({len(filtered_notebooks)})")
st.markdown("")

# Display notebooks in card grid (3 per row)
for i in range(0, len(filtered_notebooks), 3):
    cols = st.columns(3, gap="large")
    
    for j, col in enumerate(cols):
        if i + j >= len(filtered_notebooks):
            break
        
        nb_path = filtered_notebooks[i + j]
        stats = nb_path.stat()
        size_kb = stats.st_size / 1024
        modified_dt = datetime.fromtimestamp(stats.st_mtime)
        
        # Human-readable time
        if HUMANIZE_AVAILABLE:
            modified_str = humanize.naturaltime(modified_dt)
        else:
            modified_str = modified_dt.strftime("%Y-%m-%d %H:%M")
        
        tags = generate_tags(nb_path.name)
        
        with col:
            # Card container
            with st.container():
                st.markdown(f"### 📓 {nb_path.stem}")
                
                # Tags
                tag_html = " ".join([f'<span style="background-color: #1f77b4; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; margin-right: 4px;">{tag}</span>' for tag in tags])
                st.markdown(tag_html, unsafe_allow_html=True)
                
                st.markdown("")
                
                # Metadata
                st.caption(f"⏰ {modified_str}")
                st.caption(f"💾 {size_kb:.1f} KB")
                
                st.markdown("")
                
                # Buttons
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button("👁️ View", key=f"view_{nb_path.name}", use_container_width=True):
                        st.session_state['selected_notebook'] = nb_path
                        st.session_state['view_mode'] = 'reader'
                        st.rerun()
                
                with col_b:
                    if st.button("🔬 Summary", key=f"summary_{nb_path.name}", use_container_width=True):
                        st.session_state['show_summary'] = nb_path
                        st.rerun()
                
                if st.button("📂 JupyterLab", key=f"jupyter_{nb_path.name}", use_container_width=True):
                    if is_port_in_use(JUPYTER_PORT):
                        st.info(f"✅ Open http://localhost:{JUPYTER_PORT}")
                    else:
                        try:
                            subprocess.Popen(["jupyter-lab", str(nb_path)], cwd=str(PROJECT_ROOT))
                            st.success("✅ Launching JupyterLab...")
                        except FileNotFoundError:
                            st.error("❌ JupyterLab not found")
                
                st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# AI SUMMARY MODAL
# ═══════════════════════════════════════════════════════════════════

if 'show_summary' in st.session_state and st.session_state.get('show_summary'):
    st.markdown("---")
    st.markdown("## 🤖 AI Notebook Analysis")
    
    nb_path = st.session_state['show_summary']
    
    try:
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        
        summary_text = generate_summary(nb)
        
        st.markdown(f"### 📄 {nb_path.name}")
        st.markdown(summary_text)
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("✖️ Close", use_container_width=True):
                st.session_state['show_summary'] = None
                st.rerun()
        with col2:
            if st.button("👁️ View Full Notebook", use_container_width=True):
                st.session_state['selected_notebook'] = nb_path
                st.session_state['view_mode'] = 'reader'
                st.session_state['show_summary'] = None
                st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error analyzing notebook: {e}")
        if st.button("✖️ Close"):
            st.session_state['show_summary'] = None
            st.rerun()
    
    st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# NOTEBOOK READER VIEW
# ═══════════════════════════════════════════════════════════════════

if st.session_state.get('view_mode') == 'reader' and 'selected_notebook' in st.session_state:
    st.markdown("---")
    st.markdown("## 📖 Notebook Reader")
    
    nb_path = st.session_state['selected_notebook']
    
    # Header
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        st.markdown(f"### 📓 {nb_path.name}")
    
    with col2:
        if st.button("⬅️ Back to Grid"):
            st.session_state['view_mode'] = None
            st.rerun()
    
    with col3:
        if st.button("📂 JupyterLab"):
            if is_port_in_use(JUPYTER_PORT):
                st.info(f"Open: http://localhost:{JUPYTER_PORT}")
            else:
                try:
                    subprocess.Popen(["jupyter-lab", str(nb_path)], cwd=str(PROJECT_ROOT))
                    st.success("✅ Launching...")
                except:
                    st.error("❌ Launch failed")
    
    with col4:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    st.markdown("---")
    
    # Rendering options
    with st.expander("⚙️ Rendering Options", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            show_input = st.checkbox("Show code cells", value=True)
        with col2:
            show_input_prompt = st.checkbox("Show input prompts", value=False)
        with col3:
            show_output_prompt = st.checkbox("Show output prompts", value=False)
    
    # Load and render
    try:
        with st.spinner("🔄 Loading notebook..."):
            with open(nb_path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)
            
            # Convert to HTML
            html_exporter = HTMLExporter()
            html_exporter.exclude_input = not show_input
            html_exporter.exclude_input_prompt = not show_input_prompt
            html_exporter.exclude_output_prompt = not show_output_prompt
            
            body, _ = html_exporter.from_notebook_node(nb)
            
            # Enhanced CSS
            custom_css = """
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                }
                .jp-RenderedHTMLCommon {
                    font-size: 15px;
                    line-height: 1.6;
                }
                .jp-RenderedMarkdown {
                    padding: 15px;
                    background-color: #ffffff;
                }
                .jp-RenderedMarkdown h1 {
                    color: #1f77b4;
                    border-bottom: 2px solid #1f77b4;
                    padding-bottom: 10px;
                }
                .jp-RenderedMarkdown h2 {
                    color: #ff7f0e;
                    margin-top: 30px;
                }
                pre {
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #1f77b4;
                    overflow-x: auto;
                    font-size: 13px;
                }
                code {
                    background-color: #f8f9fa;
                    padding: 3px 6px;
                    border-radius: 4px;
                    font-size: 13px;
                    color: #d63384;
                }
                .jp-OutputArea-output {
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    margin-top: 10px;
                }
                img {
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15px 0;
                }
                th, td {
                    border: 1px solid #dee2e6;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f8f9fa;
                    font-weight: 600;
                }
                .jp-Cell {
                    margin-bottom: 20px;
                }
            </style>
            """
            
            full_html = custom_css + body
            
            # Render with responsive height
            st.components.v1.html(full_html, height=1400, scrolling=True)
            
    except Exception as e:
        st.error(f"❌ **Error loading notebook:** {e}")
        st.exception(e)
        
        if st.button("⬅️ Back to Grid"):
            st.session_state['view_mode'] = None
            st.rerun()

# ═══════════════════════════════════════════════════════════════════
# FUTURE: KERNEL GATEWAY EXECUTION
# ═══════════════════════════════════════════════════════════════════

# TODO: Implement safe notebook execution via Kernel Gateway
# from nbclient import NotebookClient
#
# def execute_notebook_safely(nb_path):
#     """
#     Execute notebook in isolated kernel for safe execution.
#     Requires: jupyter-kernel-gateway
#     """
#     with open(nb_path) as f:
#         nb = nbformat.read(f, as_version=4)
#     
#     client = NotebookClient(nb, timeout=600, kernel_name='python3')
#     client.execute()
#     
#     return nb
#
# # UI Component:
# if st.button("▶️ Run Notebook (Safe Mode)"):
#     with st.spinner("Executing notebook..."):
#         executed_nb = execute_notebook_safely(nb_path)
#         st.success("✅ Execution complete!")
#         # Re-render with outputs

# ═══════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")

footer_cols = st.columns([3, 1, 1])

with footer_cols[0]:
    st.caption(f"📁 Notebooks Directory: `{NOTEBOOKS_DIR.relative_to(PROJECT_ROOT)}`")

with footer_cols[1]:
    jupyter_url = f"http://localhost:{JUPYTER_PORT}"
    if is_port_in_use(JUPYTER_PORT):
        st.caption(f"🟢 [JupyterLab]({jupyter_url})")
    else:
        st.caption("⚪ JupyterLab stopped")

with footer_cols[2]:
    st.caption(f"v2.1.2 | Advanced Viewer")
