from rich.console import Console
from rich.markdown import Markdown

console = Console()

markdown_content = """The following interview is an excerpt from the 4/16/17�049 Incident Report. The interview was conducted by Dr. Elijah Itkin, and took place three weeks after the start of the initial investigation.
>
> **Date:** 5/7/17
>
> **Interviewer:** Dr. Elijah Itkin
>
> **Interviewee:** SCP-049
>
> [BEGIN LOG]
>
> **Dr. Itkin:** SCP-049, we are conducting this interview to close out our investigation of your actions taken on April 16th that resulted in the death of a staff member. Do you have any comments to make?
>
> **SCP-049:** Only that I look forward to the day when you will allow me to resume my work! I have spent the last few weeks compiling my notes and constructing a new theory for how the Pestilence was able to infect someone in such an insidious manner that I nearly couldn't detect it.
>
> **Dr. Itkin:** Have you experienced any remorse for your actions? For the death of Dr. Hamm?
>
> **SCP-049:** (*Waves his hand*) Ah, yes. Well, the death of a colleague is always regrettable, but in the face of the Pestilence we must be *swift*, doctor, and act without hesitation.
>
> **Dr. Itkin:** Dr. Sherman noted in his report that you seemed to be mournful during your initial interview.
>
> **SCP-049:** Mourn- (*Pauses*) Perhaps. I had not thought that� It is lamentable that a fellow doctor became infected, but the work continues. Regrettable as� as it was, Dr. Hamm's death provided important insight. Living human subjects are the only way to proceed forward, I am decided. My cure is of little use on dead flesh, and I have gleaned all I can from your generous supply of corpses. My desires turn towards tending to those still living who suffer from the disease.
>
> **Dr. Itkin:** I'm afraid you're going to be disappointed.
>
> **SCP-049:** (*Laughs*)
Oh doctor, I wouldn't be so sure.
>
> [END LOG]
>

"""

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