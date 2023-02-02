import os
import argparse
import logging
import shutil
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="Nombre de la libreria resultante", default = "LibraryCustom")
    parser.add_argument("-lb", "--Librarys", help="Directorio donde esta ubicado el listado de librerias", default = "lib")
    parser.add_argument("-o", "--out", help="Directorio de salida de la libreria", default = "out")
    parser.add_argument("-dg", "--debug", help="Activacion de consola para arreglar errores", default = False)
    args = parser.parse_args()
    return args
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
    for namecomponent in listcomponents:
        newpath = os.path.join(pathlibs, namecomponent)
        newpath = os.path.join(newpath, os.listdir(newpath)[1])
        newpath = os.path.join(newpath, os.listdir(newpath)[0])
        newpath = os.path.join(newpath, os.listdir(newpath)[0])#encontrammos lib con 0
        #process file
    return True
if __name__=="__main__":
    args = get_args()
