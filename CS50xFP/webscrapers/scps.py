from bs4 import BeautifulSoup
import requests
import subprocess

# page to get
url = "https://scp-wiki.wikidot.com/scp-049"

# get page content
req = requests.get(url)
soup = BeautifulSoup(req.content, "html.parser")

# filter just key div
pc = soup.find("div", id="page-content")

# apply Perl filter
result = subprocess.run(
    ["perl", "scps_filter.pl"], # we're running a perl script called scps_filter.pl
    input=str(pc).encode("utf-8"), # convert html to a str, encode, and pass as input
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# check for errors
if result.returncode != 0:
    print(f"Error with Perl filtering: {result.stderr.decode()}")

else:
    # decode output
    filtered_pc = result.stdout.decode("utf-8")

    with open("049.html", "w", encoding="utf-8") as file:
        file.write(filtered_pc)

    # convert back to soup
    pc = BeautifulSoup(filtered_pc, "html.parser")

# get all text tags
tags = pc.find_all(["p", "li", "blockquote"]) # type: ignore

# get all page text
text: list[str] = []

for tag in tags:
   #print (f"Tag: {tag.name} | Attributes: {tag.attrs}") # type: ignore
   for txt in tag.stripped_strings:
      #print(txt)
      text.append(txt)

# vars to store what matter
item_num = ""
obj_class = ""
scps = ""
desc = ""
addenda: list[str] = []
addendum = "" # write addendum before appending it to addenda
addenda_names: list[str] = []

# flags to prevent excessive looping
writing_item_num = False
writing_obj_class = False
writing_scps = False
writing_desc = False
writing_addendum = False

for i, string in enumerate(text):
    if string == "Item #:": # get item num
        writing_item_num = True

    elif string == "Object Class:": # get obj class
        writing_obj_class = True

    # now most of the rest of the doc is important
    elif string == "Special Containment Procedures:":
        writing_scps = True
   
        # rip containment procedures
        j = i + 1
        string = text[j]
        scps = string
        j += 1
        string = text[j]

        while string != "Description:":
            scps = f"{scps}\n{string}"
            j += 1
            string = text[j]

        # now, get description
        j += 1
        string = text[j]
        desc = string
        j += 1
        string = text[j]

        # go till we hit an addendum
        while "Addendum" not in string:
            if string == "«":
                break
            desc = f"{desc}\n{string}"
            j += 1
            #print(string)
            string = text[j]

        # now get the addenda
        while string != "«": # arrow at bottom of page

            if "Addendum" in string: # beginning of new addendum
                addenda_names.append(string)
                j += 1
                string = text[j]

            # until we hit a new addendum
            addendum = string # store text for addendum
            j += 1
            string = text[j]

            while "Addendum" not in string:
                if string == "«":
                    break
                addendum = f"{addendum}\n{string}"
                j += 1
                string = text[j]
                addenda.append(addendum)


    break # we have all we need don't keep looking

# format stuff

# for all strings, replace "\n" with "<br>\n" (md syntax)
scps = scps.replace("\n", "<br>\n")
desc = desc.replace("\n", "<br>\n")
for i, addendum in enumerate(addenda):
   addenda[i] = addendum.replace("\n", "<br>\n")

# save to file
with open("049.md", "w", encoding="utf-8") as file:
    pass

with open("049.md", "a", encoding="utf-8") as file:
    file.write("# SCP Info Found:<br>\n")
    file.write(f"#### Item #: {item_num}<br>\n")
    file.write(f"#### Object Class: {obj_class}<br>\n")
    file.write(f"### Special Containment Proceures:<br>\n{scps}<br>\n")
    file.write(f"### Description:<br>\n{desc}<br>\n")
    for i, addendum in enumerate(addenda):
        file.write(f"### {addenda_names[i]}<br>\n")
        file.write(f"{addendum}<br>\n")