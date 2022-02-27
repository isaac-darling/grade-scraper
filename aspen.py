import requests as r
import lxml.html as xml
from bs4 import BeautifulSoup as bsoup
from pathlib import Path
import json as j
import os

#auth and grades json documents must be stored in a directory named "json" that is held within the same parent directory as this python script
#text should be a text document in the same directory as this python script
#fill in the empty auth fields for your json file appropriately

def scrape_aspen(auth_doc , class_num):
    AUTH = Path(str(Path(__file__).parents[0]) + f"/json/{auth_doc}.json")
    with open(AUTH) as f:
        file = j.load(f)
        username = file["user"]
        password = file["pass"]

    with r.sessions.Session() as SESSION:
        login = SESSION.get("https://aspen.cps.edu/aspen/logon.do")
        login_html = xml.fromstring(login.text)
        hidden_inputs = login_html.xpath(r"//form//input[@type='hidden']")
        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}
        form["username"] = username
        form["password"] = password
        gate = SESSION.post("https://aspen.cps.edu/aspen/logon.do" , data = form)
        if str(gate) == "<Response [200]>":
            ASPEN = SESSION.get("https://aspen.cps.edu/aspen/portalClassList.do?navkey=academics.classes.list")
            SITE = bsoup(ASPEN.text , "html.parser")
            td = SITE.find_all("td" , class_ = "pointer" , onmouseout = "this.className = 'pointer'")
            classes = []
            for item in td:
                end = str(item).find("</a>")
                start = str(item).find(")\">") + 3
                if "Colloquium" not in str(item)[start:end].strip():
                    classes.append(str(item)[start:end].strip())
            td_nowrap = SITE.find_all("td" , nowrap = True)
            grades = []
            for item in td_nowrap:
                try:
                    grade = float(item.string.strip())
                    if "." in str(item.string.strip()):
                        grades.append(grade)
                except:
                    pass
            data = dict(zip(classes[:int(class_num)] , grades))
        else:
            print(gate)
            return
        print("<Successfully terminated connection>")
        return data

def json_port(grades_doc , data):
    GRADES = Path(str(Path(__file__).parents[0]) + f"/json/{grades_doc}.json")
    with open(GRADES , "r+") as f:
        f.truncate(0)
        f.write(str(data).replace("\'" , "\""))
    print(f"<Grades delivered to {grades_doc}.json>")

def readable(json , text):
    JSON = Path(str(Path(__file__).parents[0]) + f"/json/{json}.json")
    TEXT = Path(str(Path(__file__).parents[0]) + f"/{text}.txt")
    with open(JSON) as f:
        file = dict(j.load(f))
        with open(TEXT , "r+") as t:
            t.truncate(0)
            for i in range(len(file.keys())):
                if i != len(file.keys()) - 1:
                    t.write(f"{list(file.keys())[i]}: {list(file.values())[i]}\n")
                else:
                    t.write(f"{list(file.keys())[i]}: {list(file.values())[i]}")
    os.startfile(TEXT)

json_port("grades" , scrape_aspen("a" , 7))
readable("grades" , "grades")
input()