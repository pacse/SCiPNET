from rich.console import Console
from rich.markdown import Markdown

console = Console()

with open("./deepwell/scps/049/addenda/Addendum%20049.4%3A%20Post-Incident%20Report%20Interview.md") as f:
    markdown_content = f.read()

md = Markdown(markdown_content)

console.print(md)
'''

from urllib.parse import quote
from urllib.parse import unquote

string = "Addendum 049.3: 04/16/2017 Incident"

print(f"Before: {string}")
string = quote(string, safe="")
print(f"After: {string}")
string = unquote(string)
print(f"Reversed: {string}")
'''