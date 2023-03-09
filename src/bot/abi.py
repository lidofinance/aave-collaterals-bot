"""Simple helpers for ABI loading from JSON files"""

import os
from pathlib import Path

ABI_HOME = Path(os.path.dirname(__file__), "abis")


def load_abi(abi_name: str) -> str:
    """Load ABI from JSON file"""
    with open(ABI_HOME / abi_name, encoding="utf-8") as f:
        return f.read()


LendingPool = load_abi("LendingPool.json")
Oracle = load_abi("Oracle.json")
ERC20 = load_abi("ERC20.json")
