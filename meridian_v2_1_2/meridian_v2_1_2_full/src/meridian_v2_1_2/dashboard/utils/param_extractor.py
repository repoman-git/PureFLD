"""
Parameter Extractor

Extract and update parameters from notebook cells.
"""

import ast
from typing import Dict, Any, Optional


def extract_params(cell_src: str) -> Optional[Dict[str, Any]]:
    """
    Extract parameters from code cell source.
    
    Looks for: params = { ... }
    
    Args:
        cell_src: Source code of cell
    
    Returns:
        Dictionary of parameters or None
    """
    try:
        tree = ast.parse(cell_src)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'params':
                        if isinstance(node.value, ast.Dict):
                            params = {}
                            for k, v in zip(node.value.keys, node.value.values):
                                if isinstance(k, ast.Constant):
                                    key = k.value
                                    value = ast.literal_eval(ast.unparse(v))
                                    params[key] = value
                            return params
        return None
    except:
        return None


def update_params_in_cell(cell_src: str, updated_params: Dict[str, Any]) -> str:
    """
    Update parameters in cell source code.
    
    Args:
        cell_src: Original cell source
        updated_params: New parameter values
    
    Returns:
        Updated cell source
    """
    try:
        # Simple approach: reconstruct params dict
        new_params_str = "params = {\n"
        for key, value in updated_params.items():
            if isinstance(value, str):
                new_params_str += f"    '{key}': '{value}',\n"
            elif isinstance(value, bool):
                new_params_str += f"    '{key}': {value},\n"
            else:
                new_params_str += f"    '{key}': {value},\n"
        new_params_str += "}\n"
        
        # Try to replace existing params assignment
        if 'params = {' in cell_src:
            # Find the params dict and replace it
            lines = cell_src.split('\n')
            new_lines = []
            in_params = False
            brace_count = 0
            
            for line in lines:
                if 'params = {' in line and not in_params:
                    new_lines.append(new_params_str.rstrip())
                    in_params = True
                    brace_count = line.count('{') - line.count('}')
                    continue
                
                if in_params:
                    brace_count += line.count('{') - line.count('}')
                    if brace_count <= 0:
                        in_params = False
                    continue
                
                new_lines.append(line)
            
            return '\n'.join(new_lines)
        else:
            # No params found, prepend
            return new_params_str + "\n" + cell_src
            
    except Exception as e:
        print(f"Error updating params: {e}")
        return cell_src


