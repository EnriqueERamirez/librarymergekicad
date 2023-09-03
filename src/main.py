import os
import argparse
import shutil

def path_exists(path):
    return os.path.exists(path)

def ensure_directory_exists(dir_path):
    if not path_exists(dir_path):
        os.mkdir(dir_path)

def find_footprint_path(base_path, version):
    directory = 'KiCAD' if version == 'v5' else f'KiCAD{version}'
    footprint_path = os.path.join(base_path, directory, 'footprints.pretty')
    if not os.path.exists(footprint_path):
        raise ValueError(f"Directory structure not as expected in {base_path}")
    return footprint_path

def find_symbol_path(base_path, version):
    directory = 'KiCAD' if version == 'v5' else f'KiCAD{version}'
    symbol_path_dir = os.path.join(base_path, directory)

    if version == "v5":
        file_extension = ".lib"
    else:
        file_extension = ".kicad_sym"

    symbols = [file for file in os.listdir(symbol_path_dir) if file.endswith(file_extension)]
    if not symbols:
        raise ValueError(f"Directory structure not as expected in {base_path}")
    return os.path.join(symbol_path_dir, symbols[0])

def create_front_lib(pathlibs, outdir, namelibrary, version):
    for namecomponent in os.listdir(pathlibs):
        try:
            library_dir = find_footprint_path(os.path.join(pathlibs, namecomponent), version)
            for footprint in os.listdir(library_dir):
                footprint_path = os.path.join(library_dir, footprint)
                dest_path = os.path.join(outdir, f"{namelibrary}.pretty", footprint)
                shutil.copyfile(footprint_path, dest_path)
        except Exception as e:
            print(f"Error processing {namecomponent}: {e}")

def create_symbol_lib(pathlibs, outdir, namelibrary, version):
    symbol_lib = []
    for namecomponent in os.listdir(pathlibs):
        try:
            symbol_file_path = find_symbol_path(os.path.join(pathlibs, namecomponent), version)
            with open(symbol_file_path, "r") as file:
                data = file.readlines()
            symbol_lib.extend(data)
        except Exception as e:
            print(f"Error processing {namecomponent}: {e}")

    with open(os.path.join(outdir, f"{namelibrary}.lib"), "w") as file:
        file.writelines(symbol_lib)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="Nombre de la libreria resultante", default="LibraryCustom")
    parser.add_argument("-lb", "--Librarys", help="Directorio donde esta ubicado el listado de librerias", default="lib")
    parser.add_argument("-o", "--out", help="Directorio de salida de la libreria", default="out")
    parser.add_argument("-v", "--version", help="Version de KiCad (v5 o v6)", default="v5")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    if path_exists(args.Librarys):
        ensure_directory_exists(args.out)
        ensure_directory_exists(os.path.join(args.out, args.name + ".pretty"))
        create_front_lib(args.Librarys, args.out, args.name, args.version)
        create_symbol_lib(args.Librarys, args.out, args.name, args.version)
    else:
        print(f"Error: Directory {args.Librarys} does not exist.")

