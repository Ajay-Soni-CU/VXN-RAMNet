from __future__ import annotations

def markdown_text(value:object)->str:
    return str(value).replace("\\","\\\\").replace("|","\\|").replace("`","\\`").replace("\r"," ").replace("\n"," ")

def csv_cell(value:object)->object:
    if isinstance(value,str) and value.startswith(("=","+","-","@","\t","\r")): return "'"+value
    return value
