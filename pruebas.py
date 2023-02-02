import os
pathlib = "libs\\ul_ADXL345TCCZ-EP\\KiCAD\\2022-11-04_19-26-34\\2022-11-04_19-26-34.lib"
with open(pathlib, "r") as file:
    data = file.read()
listdata = data.split("\n")
# print(listdata[(len(listdata)-3):])
print(listdata[:2])
