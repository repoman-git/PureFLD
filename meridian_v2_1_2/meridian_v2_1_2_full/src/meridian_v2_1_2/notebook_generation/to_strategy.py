"""
Notebook → Strategy Generator

Extract strategy logic from notebooks and generate Python modules.
"""

import nbformat
from pathlib import Path
from typing import Dict, Any, Optional, List
import ast
from datetime import datetime


def extract_params(cell_source: str) -> Optional[Dict[str, Any]]:
    """
    Extract parameters from a code cell.
    
    Looks for patterns like:
    params = { 'key': value, ... }
    
    Args:
        cell_source: Code cell source
    
    Returns:
        Dictionary of parameters or None
    """
    try:
        # Parse the cell as Python code
        tree = ast.parse(cell_source)
        
        # Look for assignments to 'params'
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'params':
                        # Try to evaluate the value
                        if isinstance(node.value, ast.Dict):
                            params = {}
                            for k, v in zip(node.value.keys, node.value.values):
                                if isinstance(k, ast.Constant):
                                    key = k.value
                                    # Evaluate value safely
                                    value = ast.literal_eval(ast.unparse(v))
                                    params[key] = value
                            return params
        
        return None
        
    except Exception as e:
        print(f"Error extracting params: {e}")
        return None


def extract_strategy_logic(cells: List, tag: str = "# STRATEGY_LOGIC") -> List[str]:
    """
    Extract cells marked with a special tag.
    
    Args:
        cells: List of notebook cells
        tag: Comment tag to look for
    
    Returns:
        List of code strings
    """
    logic_cells = []
    
    for cell in cells:
        if cell.cell_type == 'code' and tag in cell.source:
            # Remove the tag from the source
            source = cell.source.replace(tag, '').strip()
            if source:
                logic_cells.append(source)
    
    return logic_cells


def extract_strategy_template(notebook_path: Path) -> Dict[str, Any]:
    """
    Extract strategy information from a notebook.
    
    Args:
        notebook_path: Path to notebook file
    
    Returns:
        Dictionary with:
        - strategy_name: Inferred from filename or first markdown
        - params: Extracted parameters
        - logic: List of code blocks tagged as strategy logic
        - description: First markdown cell content
    """
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Extract strategy name from filename
        strategy_name = notebook_path.stem.replace('_', ' ').title()
        
        # Extract description from first markdown cell
        description = ""
        for cell in nb.cells:
            if cell.cell_type == 'markdown':
                description = cell.source[:500]  # First 500 chars
                break
        
        # Extract parameters
        params = None
        for cell in nb.cells:
            if cell.cell_type == 'code':
                extracted = extract_params(cell.source)
                if extracted:
                    params = extracted
                    break
        
        # Extract logic cells
        logic = extract_strategy_logic(nb.cells)
        
        return {
            'strategy_name': strategy_name,
            'params': params or {},
            'logic': logic,
            'description': description,
            'source_notebook': str(notebook_path)
        }
        
    except Exception as e:
        print(f"Error extracting strategy: {e}")
        return None


def generate_strategy_module(
    template: Dict[str, Any],
    output_path: Path,
    overwrite: bool = False
) -> bool:
    """
    Generate a Python strategy module from extracted template.
    
    Args:
        template: Template dictionary from extract_strategy_template()
        output_path: Where to save the .py file
        overwrite: Allow overwriting existing file
    
    Returns:
        bool: Success status
    """
    
    # Check if file exists
    if output_path.exists() and not overwrite:
        print(f"File exists: {output_path}")
        print("Set overwrite=True to replace it")
        return False
    
    try:
        strategy_name = template['strategy_name'].replace(' ', '')
        params = template['params']
        logic = template['logic']
        description = template['description']
        
        # Generate module content
        module_content = f'''"""
{template['strategy_name']} Strategy

Auto-generated from notebook: {template['source_notebook']}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{description[:200]}...
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


class {strategy_name}Strategy:
    """
    {template['strategy_name']} trading strategy.
    
    Generated from research notebook.
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        Initialize strategy with parameters.
        
        Args:
            params: Strategy parameters
        """
        self.params = params or {template['params']!r}
        self.name = "{template['strategy_name']}"
    
    def validate_params(self) -> bool:
        """Validate parameter ranges"""
        # TODO: Add parameter validation
        return True
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals.
        
        Args:
            data: Market data DataFrame
        
        Returns:
            Series of trading signals (-1, 0, +1)
        """
        # TODO: Implement signal generation logic
        # Extracted logic blocks below:
        
'''
        
        # Add extracted logic
        if logic:
            module_content += "\n        # Extracted from notebook:\n"
            for i, block in enumerate(logic, 1):
                module_content += f"\n        # Block {i}:\n"
                # Indent the logic
                indented = "\\n".join(f"        {line}" for line in block.split('\\n'))
                module_content += f"{indented}\\n"
        else:
            module_content += """
        # No logic blocks found (add # STRATEGY_LOGIC tag in notebook)
        signals = pd.Series(0, index=data.index)
        return signals
"""
        
        module_content += '''

    def backtest(self, data: pd.DataFrame, initial_capital: float = 100000.0):
        """
        Run a backtest on provided data.
        
        Args:
            data: Historical market data
            initial_capital: Starting capital
        
        Returns:
            Backtest results
        """
        signals = self.generate_signals(data)
        
        # Simple backtesting logic
        positions = signals.shift(1).fillna(0)
        returns = data['close'].pct_change()
        strategy_returns = positions * returns
        
        equity = initial_capital * (1 + strategy_returns).cumprod()
        
        return {
            'equity': equity,
            'signals': signals,
            'returns': strategy_returns
        }


# Convenience function
def create_strategy(params: Dict[str, Any] = None):
    """Create strategy instance"""
    return ''' + strategy_name + '''Strategy(params)


if __name__ == "__main__":
    # Example usage
    strategy = create_strategy()
    print(f"Strategy: {strategy.name}")
    print(f"Parameters: {strategy.params}")
'''
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(module_content)
        
        print(f"✅ Strategy module created: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error generating strategy module: {e}")
        return False


def notebook_to_strategy_wizard(notebook_path: Path) -> Optional[Path]:
    """
    Interactive wizard to convert notebook to strategy.
    
    Args:
        notebook_path: Source notebook
    
    Returns:
        Path to generated strategy or None
    """
    print(f"📓 Converting notebook: {notebook_path.name}")
    
    # Extract template
    template = extract_strategy_template(notebook_path)
    if not template:
        print("❌ Failed to extract strategy template")
        return None
    
    print(f"✅ Extracted strategy: {template['strategy_name']}")
    print(f"   Parameters: {len(template['params'])} found")
    print(f"   Logic blocks: {len(template['logic'])} found")
    
    # Generate output path
    strategy_name = template['strategy_name'].replace(' ', '_').lower()
    output_dir = Path(__file__).parent.parent / "strategy" / "generated"
    output_path = output_dir / f"{strategy_name}.py"
    
    print(f"📝 Output: {output_path}")
    
    # Generate
    success = generate_strategy_module(template, output_path, overwrite=False)
    
    if success:
        return output_path
    return None

