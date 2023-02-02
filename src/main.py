import os
import argparse
import logging
import shutil
def ExistlistLib(dirlibs):
    if not os.path.exists(dirlibs):
        return False
    return True
def create_dirt(outdir, namelibrary):
    #crear directorios si no existen
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    if not os.path.exists(os.path.join(outdir,namelibrary+".pretty")):
        os.mkdir(os.path.join(outdir,namelibrary+".pretty"))
    return True
def CreateLibFroont(pathlibs, outdir, namelibrary):
    listcomponents = os.listdir(pathlibs)
    for namecomponent in listcomponents:
        newpath = os.path.join(pathlibs, namecomponent)
        newpath = os.path.join(newpath, os.listdir(newpath)[1])
        newpath = os.path.join(newpath, os.listdir(newpath)[0])
        newpath = os.path.join(newpath, os.listdir(newpath)[1])#encontrammos lib con 0
        newpath = os.path.join(newpath, os.listdir(newpath)[0])
        shutil.copyfile(newpath, os.path.join(outdir, namelibrary+".pretty",f"{namecomponent}.kicad_mod"))
    return True
def CreateLibSymb(pathlibs, outdir, namelibrary):
    listcomponents = os.listdir(pathlibs)
    filelib = []
    startfilelib = []
    endfilelib = []
    for namecomponent in listcomponents:
        newpath = os.path.join(pathlibs, namecomponent)
        newpath = os.path.join(newpath, os.listdir(newpath)[1])
        newpath = os.path.join(newpath, os.listdir(newpath)[0])
        newpath = os.path.join(newpath, os.listdir(newpath)[0])#encontrammos lib con 0

        with open(newpath, "r") as file:
            data = file.read()
        listdata = data.split("\n")
        filelib = filelib + listdata[2:(len(listdata)-3)]

        startfilelib = listdata[:2]
        endfilelib = listdata[(len(listdata)-3):]
    datalib = startfilelib + filelib + endfilelib
    datalib = [x for x in datalib if x!='']
    with open(os.path.join(outdir,f"{namelibrary}.lib"), "w") as file:
        datalibstr = "\n".join(datalib)
        file.write(datalibstr)
        #process file
    return True
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="Nombre de la libreria resultante", default = "LibraryCustom")
    parser.add_argument("-lb", "--Librarys", help="Directorio donde esta ubicado el listado de librerias", default = "lib")
    parser.add_argument("-o", "--out", help="Directorio de salida de la libreria", default = "out")
    parser.add_argument("-dg", "--debug", help="Activacion de consola para arreglar errores", default = False)
    args = parser.parse_args()
    return args

if __name__=="__main__":
    args = get_args()
    if ExistlistLib(args.Librarys):
        create_dirt(args.out, args.name)
        CreateLibFroont(args.Librarys, args.out, args.name)
        CreateLibSymb(args.Librarys, args.out, args.name)
