from bs4 import BeautifulSoup
from typing import cast
from json import dumps

# load html from file, thanks curl :-)
print("Loading page . . .")

with open("sites-page.html", "r", encoding="utf-8") as f:
    page = f.read()

# & soup
print("Creating soup . . .")

soup = BeautifulSoup(page, "html.parser")

# filter soup
print(f"Finding and filtering page content . . .")

sieved_soup = BeautifulSoup(str(soup.find("div", class_="site-grid")), "html.parser")

# remove doclinks for better text capture
for dl in sieved_soup.find_all("div", class_="doc-link"):
    dl.decompose()

# and collapsables
for collapse in sieved_soup.find_all("div", class_="collapsible-block"):
    collapse.decompose()

with open("sites.html", "w", encoding="utf-8") as f:
    f.write(str(sieved_soup))

# get site
print("Getting site info . . .")

sites = []

for site in sieved_soup.find_all("div", class_="socontent"):
    # ==== gather info ====
    site_info = { # what we append to sites
        "name":"",
        "loc":"",
        "desc":""
    }
    site = cast(BeautifulSoup, site)

    # get site name
    s_name = site.find("h1")
    if s_name:
        for txt in s_name.stripped_strings:
            site_info["name"] = f"{site_info['name']} {txt}" if site_info["name"] != "" else txt

    else:
        print(f"WARNING: NO SITE NAME FOUND\nSite soup:\n{site}")

    # get p tags
    p = site.find_all("p")

    # validate
    assert len(p) >= 2, f"NOT ENOUGH <p> TAGS, LEN {len(p)}\nFound tags:\n{p}\nSite soup:\n{site}"

    # get location
    for txt in p[0].stripped_strings:
        site_info["loc"] = f"{site_info['loc']}{txt}" if site_info["loc"] != "" else txt

    # remove "Location:"
    site_info["loc"] = site_info["loc"].replace("Location:", "")

    # get desc (and rest of p_tags)
    for tag in p[1:]:
        for txt in tag.stripped_strings:
            site_info["desc"] = f"{site_info['desc']}{txt}" if site_info["desc"] != "" else txt

    sites.append(site_info)

# print sites and save

print("Saving Sites as JSON . . .")

# open file
f = open("sites.json", "w")

f.write("[\n") # make syntax happy

# for all sites
for i, site in enumerate(sites):
    # convert site data to json
    json = dumps(site, indent=4) # use indent for readability

    # save to file
    f.write(f"{json}")

    # make syntax happy
    if i != len(sites) - 1:
        f.write(",")

    f.write("\n")

f.write("]") # make syntax happy

f.close()

print("JSON saved\nDone ╰(*°▽°*)╯")
