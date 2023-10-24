import requests
import re
from lxml import etree
import zipfile
from lxml.etree import ParserError
import os
import glob
import csv
from xlsxwriter.workbook import Workbook

URL = "https://docs.google.com/spreadsheets/d/1bKinOo7qlOW2zSFKqofkCZ9ufpCAesO964AUIHH7JEM/"


def download_table() -> None:
    urlCS = "https://www.cs.vsu.ru/2020/09/rasp/"
    try:
        parser = etree.HTMLParser()
        dom = etree.HTML(requests.get(urlCS).content, parser)
    except ParserError as e:
        print(e)
    idTable = re.findall("\/d\/(.*?)\/", ",".join(dom.xpath('//a/@href')))[0]
    googleURL = f"https://docs.google.com/spreadsheets/d/{idTable}/export?format=zip&id={idTable}"
    with open("temp.zip", "wb") as f:
        f.write(requests.get(googleURL).content)
    with zipfile.ZipFile("temp.zip") as f:
        f.extract("Расписание (бак., спец.).html")
        f.extract("Расписание (маг.).html")
        f.extract("Календарь 2023.html") # TODO

    os.remove("temp.zip")
    # TODO remove temps


def parse(filename):
    try:
        parser = etree.HTMLParser()
        with open(filename, encoding="utf-8") as f:
            dom = etree.HTML(f.read(), parser)
    except ParserError as e:
        print(e)

    data = {}
    table = dom.xpath('/html/body/div/table/tbody')[0].getchildren()
    maxRows = len(table)
    maxCols = 0
    for element in table[0].getchildren():
        if element.tag != "td" or element.attrib["class"] == "freezebar-cell":
            continue
        if "colspan" in element.attrib:
            maxCols += int(element.attrib["colspan"])
        else:
            maxCols += 1

    table_list = [[""] * maxCols for i in range(maxRows)]
    r = 0
    for row in table:
        c = 0
        if not "style" in row.attrib or row.attrib["style"] == "height: 9px":
            if "style" in row.attrib and row.attrib["style"] == "height: 9px":
                table_list.pop()
            continue
        for col in row.getchildren():
            if col.tag != "td" or (
                    not "class"
                    in col.attrib) or col.attrib["class"] == "freezebar-cell":
                continue
            if len(table_list[r][c]) > 0:
                while c < maxCols and len(table_list[r][c]) != 0:
                    c += 1
            text = col.text
            if text == None:
                text = ""
            cols = int(col.attrib["colspan"] if "colspan" in col.attrib else 1)
            rows = int(col.attrib["rowspan"] if "rowspan" in col.attrib else 1)
            for i1 in range(cols):
                for i2 in range(rows):
                    table_list[r + i2][c + i1] = text
            c += cols
        r += 1
    table_list.pop()
    return table_list


def toObject(table):
    objects = dict()
    for i in range(2, len(table[0])):
        course = table[0][i].strip()
        group = table[1][i].strip()
        naprav = table[2][i].strip()
        profile = table[3][i].strip()
        timetable = {"Числитель": dict(), "Знаменатель": dict()}
        chis = True
        for d in range(4, len(table)):
            day = table[d][0].strip()
            time = table[d][1].strip()
            subject = table[d][i].strip()
            key = "Числитель" if chis else "Знаменатель"
            if not day in timetable[key]:
                timetable[key][day] = dict()
            if not time in timetable[key][day]:
                timetable[key][day][time] = subject
            chis = not chis

        if not course in objects:
            objects[course] = dict()
        if not naprav in objects[course]:
            objects[course][naprav] = dict()
        if not profile in objects[course][naprav]:
            objects[course][naprav][profile] = dict()
        if group in objects[course][naprav][profile]:
            objects[course][naprav][profile][re.sub("(\d+)", lambda x: f"{x.group()}.1", group)] = objects[course][naprav][profile].pop(group)
            objects[course][naprav][profile][re.sub("(\d+)", lambda x: f"{x.group()}.2", group)] = timetable
        else:
            objects[course][naprav][profile][group] = timetable

    return objects


download_table()
table_list = parse("Расписание (бак., спец.).html")
objects = toObject(table_list)
print(objects)