from rich.console import Console as C
from rich.markdown import Markdown as M

markdown_content = """
    # This is a Heading
    Rich can do a pretty *decent* job of rendering markdown.
    - This is a list item
    - This is another list item
    """

console = C()
md = M(markdown_content)

console.print(md)