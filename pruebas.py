import os
pathlibs = "libs"
listcomponents = os.listdir(pathlibs)
for namecomponent in listcomponents:
    newpath = os.path.join(pathlibs, namecomponent)
    newpath = os.path.join(newpath, os.listdir(newpath)[1])
    newpath = os.path.join(newpath, os.listdir(newpath)[0])
    newpath = os.path.join(newpath, os.listdir(newpath)[1])#encontrammos lib con 0
    newpath = os.path.join(newpath, os.listdir(newpath)[0])

    print(newpath)
for namecomponent in listcomponents:
    newpath = os.path.join(pathlibs, namecomponent)
    newpath = os.path.join(newpath, os.listdir(newpath)[1])
    newpath = os.path.join(newpath, os.listdir(newpath)[0])
    newpath = os.path.join(newpath, os.listdir(newpath)[0])#encontrammos lib con 0
    print(newpath)

print(listcomponents)
