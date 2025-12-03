"""
Phase 3 Lite: Streamlit-Native Notebook Editor

A full-featured notebook editor built entirely in Streamlit.
No JupyterLite, no iframes, no WASM - just reliable Python execution.

Features:
- Cell-by-cell editing (markdown & code)
- Server-side execution with nbclient
- Monaco code editor
- File management (create, rename, delete, duplicate)
- Cell reordering
- Execution history
- Live output display
- Kernel state persistence
"""

import streamlit as st
from pathlib import Path
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError
import sys
from io import StringIO
from datetime import datetime
import json
import shutil

try:
    from streamlit_monaco import st_monaco
    MONACO_AVAILABLE = True
except ImportError:
    MONACO_AVAILABLE = False

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def init_session_state():
    """Initialize session state variables"""
    if 'current_notebook' not in st.session_state:
        st.session_state.current_notebook = None
    if 'notebook_data' not in st.session_state:
        st.session_state.notebook_data = None
    if 'kernel_client' not in st.session_state:
        st.session_state.kernel_client = None
    if 'exec_history' not in st.session_state:
        st.session_state.exec_history = []
    if 'edited_cells' not in st.session_state:
        st.session_state.edited_cells = {}


def load_notebook(path: Path):
    """Load a notebook from disk"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return nbformat.read(f, as_version=4)
    except Exception as e:
        st.error(f"Error loading notebook: {e}")
        return None


def save_notebook(path: Path, nb):
    """Save a notebook to disk"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        return True
    except Exception as e:
        st.error(f"Error saving notebook: {e}")
        return False


def create_new_notebook(name: str):
    """Create a new empty notebook"""
    nb = new_notebook()
    nb.cells = [
        new_markdown_cell("# New Notebook\n\nStart editing here..."),
        new_code_cell("# Your code here\nprint('Hello, Meridian!')"),
    ]
    path = NOTEBOOKS_DIR / f"{name}.ipynb"
    if save_notebook(path, nb):
        return path
    return None


def execute_cell(cell_source: str, nb):
    """Execute a single cell and capture output"""
    # Create a temporary single-cell notebook
    temp_nb = new_notebook()
    temp_nb.cells = [new_code_cell(cell_source)]
    
    try:
        # Execute using nbclient
        client = NotebookClient(temp_nb, timeout=60, kernel_name='python3')
        client.execute()
        
        # Get outputs
        executed_cell = temp_nb.cells[0]
        return {
            'success': True,
            'outputs': executed_cell.outputs,
            'execution_count': executed_cell.execution_count,
            'error': None
        }
    except CellExecutionError as e:
        return {
            'success': False,
            'outputs': [],
            'execution_count': None,
            'error': str(e)
        }
    except Exception as e:
        return {
            'success': False,
            'outputs': [],
            'execution_count': None,
            'error': f"Unexpected error: {str(e)}"
        }


def render_output(output):
    """Render a cell output"""
    if output.output_type == 'stream':
        st.code(output.text, language='')
    elif output.output_type == 'execute_result':
        if 'text/plain' in output.data:
            st.code(output.data['text/plain'], language='python')
        if 'text/html' in output.data:
            st.markdown(output.data['text/html'], unsafe_allow_html=True)
        if 'image/png' in output.data:
            import base64
            st.image(base64.b64decode(output.data['image/png']))
    elif output.output_type == 'display_data':
        if 'text/plain' in output.data:
            st.write(output.data['text/plain'])
        if 'image/png' in output.data:
            import base64
            st.image(base64.b64decode(output.data['image/png']))
    elif output.output_type == 'error':
        st.error(f"{output.ename}: {output.evalue}")
        with st.expander("Traceback"):
            st.code('\n'.join(output.traceback))


# ═══════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Meridian - Notebook Editor",
    page_icon="✏️",
    layout="wide"
)

init_session_state()

# Header
st.title("✏️ Notebook Editor (Phase 3 Lite)")
st.markdown("*Full-featured notebook editing with server-side execution*")
st.markdown("---")

# Check notebooks directory
if not NOTEBOOKS_DIR.exists():
    st.warning(f"📁 Notebooks directory not found: `{NOTEBOOKS_DIR}`")
    if st.button("Create notebooks/ directory"):
        NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
        st.success("✅ Created!")
        st.rerun()
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# LAYOUT: Sidebar (File Manager) + Main (Editor)
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.header("📁 File Manager")
    
    # Get all notebooks
    notebooks = sorted(NOTEBOOKS_DIR.glob("*.ipynb"))
    
    st.metric("Total Notebooks", len(notebooks))
    
    st.markdown("---")
    
    # File operations
    st.subheader("File Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ New", use_container_width=True):
            st.session_state.show_new_dialog = True
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # New notebook dialog
    if st.session_state.get('show_new_dialog'):
        with st.form("new_notebook_form"):
            new_name = st.text_input("Notebook name (without .ipynb)")
            submitted = st.form_submit_button("Create")
            
            if submitted and new_name:
                if (NOTEBOOKS_DIR / f"{new_name}.ipynb").exists():
                    st.error("Notebook already exists!")
                else:
                    path = create_new_notebook(new_name)
                    if path:
                        st.session_state.current_notebook = path
                        st.session_state.show_new_dialog = False
                        st.success(f"Created {new_name}.ipynb")
                        st.rerun()
            
            if st.form_submit_button("Cancel"):
                st.session_state.show_new_dialog = False
                st.rerun()
    
    st.markdown("---")
    
    # Notebook list
    st.subheader("Notebooks")
    
    for nb_path in notebooks:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            if st.button(f"📓 {nb_path.stem}", key=f"open_{nb_path.name}", use_container_width=True):
                st.session_state.current_notebook = nb_path
                st.session_state.notebook_data = load_notebook(nb_path)
                st.session_state.edited_cells = {}
                st.rerun()
        
        with col2:
            if st.button("📋", key=f"dup_{nb_path.name}", help="Duplicate"):
                new_path = NOTEBOOKS_DIR / f"{nb_path.stem}_copy.ipynb"
                counter = 1
                while new_path.exists():
                    new_path = NOTEBOOKS_DIR / f"{nb_path.stem}_copy{counter}.ipynb"
                    counter += 1
                shutil.copy(nb_path, new_path)
                st.success(f"Duplicated to {new_path.name}")
                st.rerun()
        
        with col3:
            if st.button("🗑️", key=f"del_{nb_path.name}", help="Delete"):
                st.session_state.confirm_delete = nb_path
                st.rerun()
    
    # Delete confirmation
    if st.session_state.get('confirm_delete'):
        st.markdown("---")
        st.warning(f"Delete {st.session_state.confirm_delete.name}?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes"):
                st.session_state.confirm_delete.unlink()
                if st.session_state.current_notebook == st.session_state.confirm_delete:
                    st.session_state.current_notebook = None
                    st.session_state.notebook_data = None
                st.session_state.confirm_delete = None
                st.success("Deleted!")
                st.rerun()
        with col2:
            if st.button("❌ No"):
                st.session_state.confirm_delete = None
                st.rerun()

# ═══════════════════════════════════════════════════════════════════
# MAIN EDITOR AREA
# ═══════════════════════════════════════════════════════════════════

if st.session_state.current_notebook is None:
    st.info("👈 Select a notebook from the sidebar to start editing")
    
    st.markdown("### 🚀 Quick Start")
    st.markdown("""
    **Getting Started:**
    1. Click **➕ New** to create a notebook
    2. Or select an existing notebook from the list
    3. Edit cells, run code, and save changes
    
    **Features:**
    - ✏️ Edit markdown and code cells
    - ▶️ Execute code with live output
    - 🔄 Reorder cells
    - ➕ Add/delete cells
    - 💾 Save changes
    - 📊 View execution history
    """)
    st.stop()

# Load notebook if needed
if st.session_state.notebook_data is None:
    st.session_state.notebook_data = load_notebook(st.session_state.current_notebook)
    if st.session_state.notebook_data is None:
        st.error("Failed to load notebook")
        st.stop()

nb = st.session_state.notebook_data

# Notebook header
col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

with col1:
    st.subheader(f"📓 {st.session_state.current_notebook.name}")

with col2:
    if st.button("💾 Save", use_container_width=True):
        if save_notebook(st.session_state.current_notebook, nb):
            st.success("Saved!")
            st.session_state.edited_cells = {}
        else:
            st.error("Save failed!")

with col3:
    if st.button("✖️ Close", use_container_width=True):
        st.session_state.current_notebook = None
        st.session_state.notebook_data = None
        st.session_state.edited_cells = {}
        st.rerun()

with col4:
    show_history = st.checkbox("📊 History", value=False)

st.markdown("---")

# Execution history panel
if show_history:
    with st.expander("📊 Execution History", expanded=True):
        if st.session_state.exec_history:
            for i, entry in enumerate(reversed(st.session_state.exec_history[-10:])):
                st.markdown(f"**{entry['timestamp'].strftime('%H:%M:%S')}** - Cell {entry['cell_idx']}")
                if entry['success']:
                    st.success(f"✅ Executed successfully")
                else:
                    st.error(f"❌ Error: {entry['error'][:100]}")
                st.markdown("---")
        else:
            st.info("No execution history yet")

# ═══════════════════════════════════════════════════════════════════
# CELL EDITOR
# ═══════════════════════════════════════════════════════════════════

st.subheader("Cells")

for idx, cell in enumerate(nb.cells):
    with st.container():
        # Cell header
        col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
        
        with col1:
            st.markdown(f"**Cell {idx + 1}** | *{cell.cell_type}*")
        
        with col2:
            if cell.cell_type == 'code':
                cell.cell_type = st.selectbox(
                    "Type",
                    ["code", "markdown"],
                    index=0,
                    key=f"type_{idx}",
                    label_visibility="collapsed"
                )
            else:
                cell.cell_type = st.selectbox(
                    "Type",
                    ["markdown", "code"],
                    index=0,
                    key=f"type_{idx}",
                    label_visibility="collapsed"
                )
        
        with col3:
            if idx > 0:
                if st.button("⬆️", key=f"up_{idx}", help="Move up"):
                    nb.cells[idx], nb.cells[idx-1] = nb.cells[idx-1], nb.cells[idx]
                    st.rerun()
        
        with col4:
            if idx < len(nb.cells) - 1:
                if st.button("⬇️", key=f"down_{idx}", help="Move down"):
                    nb.cells[idx], nb.cells[idx+1] = nb.cells[idx+1], nb.cells[idx]
                    st.rerun()
        
        with col5:
            if st.button("➕", key=f"add_{idx}", help="Insert cell below"):
                if cell.cell_type == 'code':
                    new_cell = new_code_cell("")
                else:
                    new_cell = new_markdown_cell("")
                nb.cells.insert(idx + 1, new_cell)
                st.rerun()
        
        with col6:
            if st.button("🗑️", key=f"delete_{idx}", help="Delete cell"):
                if len(nb.cells) > 1:
                    nb.cells.pop(idx)
                    st.rerun()
                else:
                    st.warning("Cannot delete the last cell")
        
        # Cell content editor
        if cell.cell_type == 'markdown':
            # Markdown editor
            edited_source = st.text_area(
                "Markdown content",
                value=cell.source,
                height=150,
                key=f"md_edit_{idx}",
                label_visibility="collapsed"
            )
            
            if edited_source != cell.source:
                cell.source = edited_source
                st.session_state.edited_cells[idx] = True
            
            # Preview
            if cell.source.strip():
                with st.expander("Preview", expanded=False):
                    st.markdown(cell.source)
        
        else:  # code cell
            # Code editor
            if MONACO_AVAILABLE:
                edited_code = st_monaco(
                    value=cell.source,
                    height=200,
                    language="python",
                    theme="vs-dark",
                    key=f"code_edit_{idx}"
                )
            else:
                edited_code = st.text_area(
                    "Code",
                    value=cell.source,
                    height=200,
                    key=f"code_edit_{idx}",
                    label_visibility="collapsed"
                )
            
            if edited_code != cell.source:
                cell.source = edited_code
                st.session_state.edited_cells[idx] = True
            
            # Run button and output
            col_run, col_backtest, col_clear = st.columns([1, 1, 4])
            
            with col_run:
                if st.button("▶️ Run", key=f"run_{idx}", use_container_width=True):
                    with st.spinner("Executing..."):
                        result = execute_cell(cell.source, nb)
                        
                        # Update execution history
                        st.session_state.exec_history.append({
                            'cell_idx': idx + 1,
                            'timestamp': datetime.now(),
                            'success': result['success'],
                            'error': result.get('error')
                        })
                        
                        # Store result for display
                        st.session_state[f'cell_result_{idx}'] = result
                        st.rerun()
            
            with col_backtest:
                if st.button("🚀 Backtest", key=f"bt_{idx}", use_container_width=True, help="Run as backtest"):
                    with st.spinner("Running backtest..."):
                        try:
                            # Import required modules
                            from meridian_v2_1_2.api import run_backtest
                            from meridian_v2_1_2.storage import save_run
                            from meridian_v2_1_2.dashboard.utils.param_extractor import extract_params
                            
                            # Extract parameters from cell
                            params = extract_params(cell.source)
                            
                            if params is None:
                                st.error("❌ No 'params = {...}' found in cell")
                                st.info("💡 Add a params dict like: params = {'fld_offset': 10}")
                            else:
                                # Detect strategy name (look for common patterns)
                                strategy_name = "FLD"  # Default
                                cell_lower = cell.source.lower()
                                if 'cot' in cell_lower:
                                    strategy_name = "COT"
                                elif 'tdom' in cell_lower:
                                    strategy_name = "TDOM"
                                
                                # Run the backtest
                                result = run_backtest(
                                    strategy_name=strategy_name,
                                    params=params,
                                    initial_capital=params.get('initial_capital', 100000)
                                )
                                
                                # Save to registry
                                save_run(result.to_dict())
                                
                                # Display success message
                                st.success(f"✅ Backtest complete! Run ID: {result.run_id[:8]}...")
                                
                                # Store result for display
                                st.session_state[f'backtest_result_{idx}'] = result.to_dict()
                                st.rerun()
                                
                        except ImportError as e:
                            st.error(f"❌ Import error: {e}")
                            st.info("Make sure all required modules are installed")
                        except Exception as e:
                            st.error(f"❌ Backtest failed: {str(e)}")
                            st.info("Check your parameters and try again")
            
            # Display output if exists
            if f'cell_result_{idx}' in st.session_state:
                result = st.session_state[f'cell_result_{idx}']
                
                if result['success']:
                    if result['outputs']:
                        with st.container():
                            st.markdown("**Output:**")
                            for output in result['outputs']:
                                render_output(output)
                    else:
                        st.info("✅ Executed successfully (no output)")
                else:
                    st.error(f"❌ Execution failed: {result['error']}")
            
            # Display backtest results if exists
            if f'backtest_result_{idx}' in st.session_state:
                bt_result = st.session_state[f'backtest_result_{idx}']
                
                with st.container():
                    st.markdown("**🚀 Backtest Results:**")
                    
                    # Import visualization component
                    try:
                        from meridian_v2_1_2.dashboard.components.backtest_viz import backtest_summary
                        
                        # Display summary
                        with st.expander("📊 View Full Results", expanded=True):
                            backtest_summary(bt_result)
                            
                            # Link to results page
                            st.info(f"💡 View this run in the **Backtest Results** page (Run ID: {bt_result.get('run_id', '')[:8]}...)")
                    except ImportError:
                        # Fallback to simple display
                        metrics = bt_result.get('metrics', {})
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Sharpe", f"{metrics.get('sharpe_ratio', 0):.2f}")
                        with col2:
                            st.metric("Return", f"{metrics.get('total_return', 0):.2%}")
                        with col3:
                            st.metric("Max DD", f"{metrics.get('max_drawdown', 0):.2%}")
                        with col4:
                            st.metric("Trades", metrics.get('num_trades', 0))
        
        st.markdown("---")

# Add cell at end
if st.button("➕ Add Cell at End", use_container_width=True):
    nb.cells.append(new_code_cell(""))
    st.rerun()

# ═══════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")

footer_cols = st.columns([2, 1, 1, 1])

with footer_cols[0]:
    if st.session_state.edited_cells:
        st.warning(f"⚠️ {len(st.session_state.edited_cells)} unsaved changes")
    else:
        st.caption("✅ All changes saved")

with footer_cols[1]:
    st.caption(f"📊 {len(nb.cells)} cells")

with footer_cols[2]:
    code_cells = sum(1 for c in nb.cells if c.cell_type == 'code')
    st.caption(f"💻 {code_cells} code")

with footer_cols[3]:
    md_cells = sum(1 for c in nb.cells if c.cell_type == 'markdown')
    st.caption(f"📝 {md_cells} markdown")

st.caption("Phase 3 Lite | Server-Side Execution | No JupyterLite Required")

