import os
import argparse
import shutil
import re

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
        os.makedirs(dir_path, exist_ok=True)
    return True

def is_valid_library_directory(path):
    """
    Check if a path is a valid library directory (not a zip file or other invalid format).
    
    Args:
    path (str): The path to check.
    
    Returns:
    bool: True if it's a valid directory, False otherwise.
    """
    if not os.path.isdir(path):
        return False
    
    # Get the basename to check for unwanted patterns
    basename = os.path.basename(path)
    
    # Skip zip files, step files, and other non-directory formats
    invalid_extensions = ['.zip', '.step', '.stp', '.stl', '.rar', '.7z', '.tar', '.gz']
    if any(basename.lower().endswith(ext) for ext in invalid_extensions):
        return False
    
    # Skip output directory to avoid processing our own output
    if basename == 'lib' or basename.startswith('out'):
        return False
        
    return True

def find_kicad_directory(component_path, version):
    """
    Find the KiCAD directory within a component.
    Handles both nested (KiCADv6/) and flat structures.
    
    Args:
    component_path (str): The path to the component.
    version (str): The KiCad version.
    
    Returns:
    str: The path to the KiCAD directory, or the component_path if flat structure.
    """
    # Expected directory names
    directory_names = [
        'KiCAD' if version == 'v5' else f'KiCAD{version}',
        'KiCAD',  # fallback
        'kicad',
        'KICAD'
    ]
    
    # Check if nested structure exists
    for dir_name in directory_names:
        potential_path = os.path.join(component_path, dir_name)
        if os.path.isdir(potential_path):
            return potential_path
    
    # If no nested structure, return component_path (flat structure)
    return component_path

def find_footprint_path(base_path, version):
    """
    Find the path to the footprint.
    Handles both nested (KiCADv6/footprints.pretty) and flat structures.

    Args:
    base_path (str): The base path to search for the footprint.
    version (str): The version of KiCad.

    Returns:
    str: The path to the footprint.
    """
    kicad_dir = find_kicad_directory(base_path, version)
    footprint_path = os.path.join(kicad_dir, 'footprints.pretty')
    
    if os.path.exists(footprint_path):
        return footprint_path
    
    # Try flat structure - look for .kicad_mod files in the base directory
    for file in os.listdir(base_path):
        if file.endswith('.kicad_mod'):
            # Footprints exist in flat structure
            return base_path
    
    raise ValueError(f"No footprint directory found in {base_path}")

def find_symbol_path(base_path, version):
    """
    Find the path to the symbol.
    Handles both nested (KiCADv6/) and flat structures.

    Args:
    base_path (str): The base path to search for the symbol.
    version (str): The version of KiCad.

    Returns:
    str: The path to the symbol file.
    """
    kicad_dir = find_kicad_directory(base_path, version)
    
    if version == "v5":
        file_extension = ".lib"
    else:
        file_extension = ".kicad_sym"

    # Check in the kicad_dir first
    if os.path.isdir(kicad_dir):
        symbols = [file for file in os.listdir(kicad_dir) if file.endswith(file_extension)]
        if symbols:
            return os.path.join(kicad_dir, symbols[0])
    
    # Check in base_path for flat structure
    symbols = [file for file in os.listdir(base_path) if file.endswith(file_extension)]
    if symbols:
        return os.path.join(base_path, symbols[0])
    
    raise ValueError(f"No symbol file (.{file_extension}) found in {base_path}")

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
    processed_count = 0
    skipped_count = 0
    
    for namecomponent in os.listdir(pathlibs):
        component_path = os.path.join(pathlibs, namecomponent)
        
        # Skip invalid directories/files
        if not is_valid_library_directory(component_path):
            print(f"Skipping {namecomponent} (not a valid library directory)")
            skipped_count += 1
            continue
            
        try:
            library_dir = find_footprint_path(component_path, version)
            for footprint in os.listdir(library_dir):
                footprint_path = os.path.join(library_dir, footprint)
                # Only copy files, not directories
                if os.path.isfile(footprint_path):
                    dest_path = os.path.join(outdir, f"{namelibrary}.pretty", footprint)
                    shutil.copyfile(footprint_path, dest_path)
            processed_count += 1
            print(f"Processed footprints from {namecomponent}")
        except Exception as e:
            print(f"Error processing {namecomponent}: {e}")
            skipped_count += 1
    
    print(f"Footprint processing complete: {processed_count} libraries processed, {skipped_count} skipped")

def parse_kicad_sym_content(content):
    """
    Parse the content of a .kicad_sym file to extract symbols.
    
    Args:
    content (str): The content of the .kicad_sym file.
    
    Returns:
    list: List of symbol definitions
    """
    symbols = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('(symbol '):
            # Start of a symbol definition
            symbol_lines = []
            paren_count = 0
            
            # Count parentheses to find the complete symbol definition
            j = i
            while j < len(lines):
                current_line = lines[j]
                symbol_lines.append(current_line)
                
                # Count parentheses
                paren_count += current_line.count('(') - current_line.count(')')
                
                j += 1
                # If we've closed all parentheses and we're not on the first line, we're done
                if paren_count == 0 and j > i + 1:
                    break
            
            symbols.append('\n'.join(symbol_lines))
            i = j
        else:
            i += 1
    
    return symbols

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
    if version == "v5":
        create_symbol_lib_v5(pathlibs, outdir, namelibrary)
    else:
        create_symbol_lib_kicad_sym(pathlibs, outdir, namelibrary, version)

def create_symbol_lib_v5(pathlibs, outdir, namelibrary):
    """
    Create symbol library for KiCad v5 (.lib format).
    """
    symbol_lib = []
    processed_count = 0
    skipped_count = 0
    
    for namecomponent in os.listdir(pathlibs):
        component_path = os.path.join(pathlibs, namecomponent)
        
        # Skip invalid directories/files
        if not is_valid_library_directory(component_path):
            skipped_count += 1
            continue
            
        try:
            symbol_file_path = find_symbol_path(component_path, "v5")
            with open(symbol_file_path, "r", encoding='utf-8') as file:
                data = file.readlines()
            symbol_lib.extend(data)
            processed_count += 1
            print(f"Processed symbols from {namecomponent}")
        except Exception as e:
            print(f"Error processing {namecomponent}: {e}")
            skipped_count += 1

    with open(os.path.join(outdir, f"{namelibrary}.lib"), "w", encoding='utf-8') as file:
        file.writelines(symbol_lib)
    
    print(f"Symbol processing complete: {processed_count} libraries processed, {skipped_count} skipped")

def create_symbol_lib_kicad_sym(pathlibs, outdir, namelibrary, version):
    """
    Create symbol library for KiCad v6+ (.kicad_sym format).
    """
    all_symbols = []
    generator_info = None
    version_info = None
    processed_count = 0
    skipped_count = 0
    
    for namecomponent in os.listdir(pathlibs):
        component_path = os.path.join(pathlibs, namecomponent)
        
        # Skip invalid directories/files
        if not is_valid_library_directory(component_path):
            skipped_count += 1
            continue
            
        try:
            symbol_file_path = find_symbol_path(component_path, version)
            with open(symbol_file_path, "r", encoding='utf-8') as file:
                content = file.read()
            
            # Extract version and generator info from the first file
            if generator_info is None:
                version_match = re.search(r'\(version\s+(\d+)\)', content)
                generator_match = re.search(r'\(generator\s+"([^"]+)"\)', content)
                
                if version_match:
                    version_info = version_match.group(1)
                if generator_match:
                    generator_info = generator_match.group(1)
            
            # Extract symbols from the content
            symbols = parse_kicad_sym_content(content)
            all_symbols.extend(symbols)
            processed_count += 1
            print(f"Processed symbols from {namecomponent}")
            
        except Exception as e:
            print(f"Error processing {namecomponent}: {e}")
            skipped_count += 1

    # Create the combined .kicad_sym file
    output_file = os.path.join(outdir, f"{namelibrary}.kicad_sym")
    with open(output_file, "w", encoding='utf-8') as file:
        # Write header
        file.write("(kicad_symbol_lib\n")
        file.write(f"  (version {version_info or '20211014'})\n")
        file.write(f"  (generator \"{generator_info or 'kicad_symbol_editor'}\")\n")
        
        # Write all symbols
        for symbol in all_symbols:
            file.write("  " + symbol.replace('\n', '\n  ') + "\n")
        
        # Close the library
        file.write(")\n")
    
    print(f"Symbol processing complete: {processed_count} libraries processed, {skipped_count} skipped")

def move_3d_models(pathlibs, outdir):
    """
    Move all .step and .stl models to a designated models3d directory.

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

    # Supported 3D model extensions
    model_extensions = [".step", ".stp", ".stl", ".STL", ".STEP", ".STP"]
    processed_count = 0

    for namecomponent in os.listdir(pathlibs):
        component_path = os.path.join(pathlibs, namecomponent)
        
        # Only process directories
        if not os.path.isdir(component_path):
            continue
        
        # Skip invalid directories (like zip files that might appear as directories)
        if not is_valid_library_directory(component_path):
            continue
            
        for file in os.listdir(component_path):
            # Check if the file is a 3D model file
            if any(file.endswith(ext) for ext in model_extensions):
                # Define the source and destination paths
                src_path = os.path.join(component_path, file)
                dest_path = os.path.join(models3d_dir, file)
                
                # Handle file name conflicts
                counter = 1
                original_dest_path = dest_path
                while os.path.exists(dest_path):
                    name, ext = os.path.splitext(original_dest_path)
                    dest_path = f"{name}_{counter}{ext}"
                    counter += 1
                
                try:
                    # Copy the file to the models3d directory (instead of move to preserve originals)
                    shutil.copy2(src_path, dest_path)
                    print(f"Copied {file} to models3d directory as {os.path.basename(dest_path)}")
                    processed_count += 1
                except Exception as e:
                    print(f"Error copying {file}: {e}")
    
    print(f"3D model processing complete: {processed_count} files copied")

def get_args():
    """
    Get the command line arguments.

    Args:
    None

    Returns:
    argparse.Namespace: The command line arguments.
    """
    parser = argparse.ArgumentParser(description="KiCad Library Consolidation Tool")
    parser.add_argument("-n", "--name", help="Nombre de la libreria resultante", default="LibraryCustom")
    parser.add_argument("-lb", "--Librarys", help="Directorio donde esta ubicado el listado de librerias", default="lib")
    parser.add_argument("-o", "--out", help="Directorio de salida de la libreria", default="out")
    parser.add_argument("-v", "--version", help="Version de KiCad (v5, v6, v7, v8)", default="v6", 
                       choices=['v5', 'v6', 'v7', 'v8'])
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    if path_exists(args.Librarys):
        print(f"Processing libraries from: {args.Librarys}")
        print(f"Output directory: {args.out}")
        print(f"Library name: {args.name}")
        print(f"KiCad version: {args.version}")
        
        ensure_directory_exists(args.out)
        ensure_directory_exists(os.path.join(args.out, args.name + ".pretty"))
        
        print("\nCreating footprint library...")
        create_front_lib(args.Librarys, args.out, args.name, args.version)
        
        print("\nCreating symbol library...")
        create_symbol_lib(args.Librarys, args.out, args.name, args.version)
        
        print("\nProcessing 3D models...")
        move_3d_models(args.Librarys, args.out)
        
        print("\nLibrary consolidation completed!")
    else:
        print(f"Error: Directory {args.Librarys} does not exist.")
