"""Helper utilities"""
import json
from typing import Any, Dict


def safe_get(data: Dict, *keys, default=None) -> Any:
    """Safely navigate nested dictionaries"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data


def format_currency(amount: float) -> str:
    """Format amount as USD currency"""
    return f"${amount:,.2f}"


def load_json_file(filepath: str) -> Dict:
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json_file(filepath: str, data: Dict):
    """Save data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
