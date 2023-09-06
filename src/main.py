import os
import argparse
import shutil

def path_exists(path):
    """
    Check if a path exists.

    Args:
    path (str): The path to check.

    Returns:
    bool: True if the path exists, False otherwise.
    """
    return os.path.exists(path)

def ensure_directory_exists(dir_path):
    """
    Ensure that a directory exists. If it doesn't exist, create it.

    Args:
    dir_path (str): The path to the directory.

    Returns:
    bool: True if the directory exists or was created successfully, False otherwise.
    """
    if not path_exists(dir_path):
        os.mkdir(dir_path)
    return True

def find_footprint_path(base_path, version):
    """
    Find the path to the footprint.

    Args:
    base_path (str): The base path to search for the footprint.
    version (str): The version of KiCad.

    Returns:
    str: The path to the footprint.
    """
    directory = 'KiCAD' if version == 'v5' else f'KiCAD{version}'
    footprint_path = os.path.join(base_path, directory, 'footprints.pretty')
    if not os.path.exists(footprint_path):
        raise ValueError(f"Directory structure not as expected in {base_path}")
    return footprint_path

def find_symbol_path(base_path, version):
    """
    Find the path to the symbol.

    Args:
    base_path (str): The base path to search for the symbol.
    version (str): The version of KiCad.

    Returns:
    str: The path to the symbol.
    """
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
    """
    Create the front library.

    Args:
    pathlibs (str): The path to the libraries.
    outdir (str): The output directory.
    namelibrary (str): The name of the library.
    version (str): The version of KiCad.

    Returns:
    None
    """
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
    """
    Create the symbol library.

    Args:
    pathlibs (str): The path to the libraries.
    outdir (str): The output directory.
    namelibrary (str): The name of the library.
    version (str): The version of KiCad.

    Returns:
    None
    """
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
def move_step_models(pathlibs, outdir):
    """
    Move all .step models to a designated models3d directory.

    Args:
    pathlibs (str): The path to the libraries.
    outdir (str): The output directory.

    Returns:
    None
    """
    # Define the models3d directory path
    models3d_dir = os.path.join(outdir, 'models3d')
    
    # Ensure the models3d directory exists
    ensure_directory_exists(models3d_dir)

    for namecomponent in os.listdir(pathlibs):
        component_path = os.path.join(pathlibs, namecomponent)
        for file in os.listdir(component_path):
            # Check if the file is a .step file
            if file.endswith(".step"):
                # Define the source and destination paths
                src_path = os.path.join(component_path, file)
                dest_path = os.path.join(models3d_dir, file)
                
                # Move the file to the models3d directory
                shutil.move(src_path, dest_path)
                print(f"Moved {file} to models3d directory.")

def get_args():
    """
    Get the command line arguments.

    Args:
    None

    Returns:
    argparse.Namespace: The command line arguments.
    """
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
        move_step_models(args.Librarys, args.out)
    else:
        print(f"Error: Directory {args.Librarys} does not exist.")