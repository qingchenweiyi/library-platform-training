# -*- coding: utf-8 -*-
"""修复 docPr id 冲突：重新编号所有部件中的 wp:docPr id。"""
import zipfile, shutil, re, os

src = "/home/user/Doubao/chats/38446798884423426/report/班级(X班)-完整学号-姓名.docx"
tmp = src + ".tmp"

zin = zipfile.ZipFile(src, "r")
zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)

counter = [100]
def fix_xml(xml):
    def repl(m):
        counter[0] += 1
        return f'wp:docPr id="{counter[0]}"'
    return re.sub(r'wp:docPr id="\d+"', repl, xml)

for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename.endswith(".xml"):
        try:
            text = data.decode("utf-8")
            if "wp:docPr" in text:
                text = fix_xml(text)
            data = text.encode("utf-8")
        except UnicodeDecodeError:
            pass
    zout.writestr(item, data)
zin.close(); zout.close()
shutil.move(tmp, src)
print("docPr ids renumbered, max =", counter[0])
