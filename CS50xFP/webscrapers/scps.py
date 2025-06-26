from bs4 import BeautifulSoup
import requests

url = "https://scp-wiki.wikidot.com/scp-049"
req = requests.get(url)

soup = BeautifulSoup(req.content, "html.parser")

pc = soup.find("div", id="page-content")

tags = pc.find_all(["p", "li", "blockquote"]) # type: ignore

text: list[str] = []

# get all page text
for tag in tags:
   print (f"Tag: {tag.name} | Attributes: {tag.attrs}")
   for txt in tag.stripped_strings:
      print(txt)
      text.append(txt)

# vars to store what matters
item_num: str = "NULL"
obj_class: str = "NULL"
scps: str = ""
desc: str = "NULL"
addenda: list[str] = []
addenda_names: list[str] = []

for i, string in enumerate(text):
  if string == "Item #:": # get item num
    item_num = text[i+1]

  elif string == "Object Class:": # get obj class
    obj_class = text[i+1]

  # now most of the rest of the doc is important
  elif string == "Special Containment Procedures:":
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
with open("049.md", "w") as file:
    pass

with open("049.md", "a") as file:
    file.write("# SCP Info Found:<br>\n")
    file.write(f"#### Item #: {item_num}<br>\n")
    file.write(f"#### Object Class: {obj_class}<br>\n")
    file.write(f"### Special Containment Proceures:<br>\n{scps}<br>\n")
    file.write(f"### Description:<br>\n{desc}<br>\n")
    for i, addendum in enumerate(addenda):
        file.write(f"### {addenda_names[i]}<br>\n")
        file.write(f"{addendum}<br>\n")