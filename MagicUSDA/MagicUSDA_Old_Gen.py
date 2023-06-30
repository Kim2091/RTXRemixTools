import os, argparse
import xxhash
from pxr import Usd, UsdGeom, UsdShade, Sdf

suffixes = ["_normal", "_emissive", "_metallic", "_rough"]

def generate_hashes(file_path) -> str:
    # Read the file and extract the raw data. Thanks @BlueAmulet!
    with open(file_path, "rb") as file:
        data = file.read(128)

    dwHeight = int.from_bytes(data[12:16], "little")
    dwWidth = int.from_bytes(data[16:20], "little")
    pfFlags = int.from_bytes(data[80:84], "little")
    pfFourCC = data[84:88]
    bitCount = int.from_bytes(data[88:92], "little")

    mipsize = dwWidth * dwHeight
    if pfFlags & 0x4:  # DDPF_FOURCC
        if pfFourCC == b"DXT1":  # DXT1 is 4bpp
            mipsize //= 2
    elif pfFlags & 0x20242:  # DDPF_ALPHA | DDPF_RGB | DDPF_YUV | DDPF_LUMINANCE
        mipsize = mipsize * bitCount // 8

    # Read the required portion of the file for hash calculation
    with open(file_path, "rb") as file:
        file.seek(128)  # Move the file pointer to the appropriate position
        data = file.read(mipsize)

    hash_value = xxhash.xxh3_64(data).hexdigest()

    return hash_value.upper()


def write_usda_file(args, file_list, suffix=None) -> [list, list]:
    created_files  = []
    modified_files = []
    game_ready_assets_path = os.path.join(args.directory)

    # Check if there are any texture files with the specified suffix
    if suffix:
        has_suffix_files = False
        for file_name in file_list:
            if file_name.endswith(f"{suffix}.dds"):
                has_suffix_files = True
                break
        if not has_suffix_files:
            # return a blank set
            return [created_files, modified_files]

    usda_file_name = f'{args.output}{suffix if suffix else ""}.usda'
    usda_file_path = os.path.join(game_ready_assets_path, usda_file_name)

    if os.path.exists(usda_file_path):
        modified_files.append(usda_file_path)
    else:
        created_files.append(usda_file_path)

    targets = {}
    
    reference_directory = args.reference_directory if args.reference_directory else args.directory
    
    for file_name in file_list:
        if file_name.endswith(".dds"):
            name, ext = os.path.splitext(file_name)
            if "_" not in name or name.endswith("_diffuse"):
                # Check if the generate_hashes argument is specified
                if args.generate_hashes:
                    key = generate_hashes(os.path.join(reference_directory, file_name))
                else:
                    key = name
                targets[key] = name


    # Create a new stage
    stage = Usd.Stage.CreateNew(usda_file_path)

    # Modify the existing RootNode prim
    root_node_prim = stage.OverridePrim("/RootNode")

    # Add a Looks scope as a child of the RootNode prim
    looks_scope = UsdGeom.Scope.Define(stage, "/RootNode/Looks")
    
    added_targets = set()
    for value, name in targets.items():
        # We only want to generate materials for inputs that are hashes in this mode
        if args.exclude_non_hashes:
            if not name.isupper() and not len(name) == 16:
                continue

        # Check if there is a corresponding texture file for the specified suffix
        if suffix and not any(
            file_name.endswith(f"{value}{suffix}.dds") for file_name in file_list
        ):  continue
        if value in added_targets:
            continue
        else:
            added_targets.add(value)
            print(f"Adding: {value}, {name}")

        # Add a material prim as a child of the Looks scope
        material_prim = UsdShade.Material.Define(
            stage, f"/RootNode/Looks/mat_{value.upper()}"
        )
        material_prim.GetPrim().GetReferences().SetReferences([])

        # Set the shader attributes
        shader_prim = UsdShade.Shader.Define(
            stage, f"/RootNode/Looks/mat_{value.upper()}/Shader"
        )
        shader_prim.CreateInput("info:mdl:sourceAsset", Sdf.ValueTypeNames.Asset).Set(
            "AperturePBR_Opacity.mdl"
        )
        shader_output = shader_prim.CreateOutput("output", Sdf.ValueTypeNames.Token)

        if not suffix or suffix == "_diffuse":
            diffuse_texture = shader_prim.CreateInput(
                "diffuse_texture", Sdf.ValueTypeNames.Asset
            )
            diffuse_texture.Set(f"./{name}.dds")
        
        # Process each type of texture
        if not suffix or suffix == "_emissive":
            emissive_file_name = f"{value}_emissive.dds"
            if emissive_file_name in file_list:
                emissive_mask_texture = shader_prim.CreateInput(
                    "emissive_mask_texture", Sdf.ValueTypeNames.Asset
                )
                emissive_mask_texture.Set(f"./{emissive_file_name}")
                enable_emission = shader_prim.CreateInput(
                    "enable_emission", Sdf.ValueTypeNames.Bool
                )
                enable_emission.Set(True)
                emissive_intensity = shader_prim.CreateInput(
                    "emissive_intensity", Sdf.ValueTypeNames.Float
                )
                emissive_intensity.Set(5)

        if not suffix or suffix == "_metallic":
            if f"{name}_metallic.dds" in file_list:
                metallic_texture = shader_prim.CreateInput(
                    "metallic_texture", Sdf.ValueTypeNames.Asset
                )
                metallic_texture.Set(f"./{name}_metallic.dds")

        if not suffix or suffix == "_normal":
            if f"{name}_normal.dds" in file_list:
                normalmap_texture = shader_prim.CreateInput(
                    "normal_texture", Sdf.ValueTypeNames.Asset
                )
                normalmap_texture.Set(f"./{name}_normal.dds")

        if not suffix or suffix == "_rough":
            if f"{name}_rough.dds" in file_list:
                reflectionroughness_texture = shader_prim.CreateInput(
                    "roughness_texture", Sdf.ValueTypeNames.Asset
                )
                reflectionroughness_texture.Set(f"./{name}_rough.dds")

        # Connect shader output to material inputs
        material_prim.CreateInput(
            "mdl:displacement", Sdf.ValueTypeNames.Token
        ).ConnectToSource(shader_output)
        material_prim.CreateInput(
            "mdl:surface", Sdf.ValueTypeNames.Token
        ).ConnectToSource(shader_output)
        material_prim.CreateInput(
            "mdl:volume", Sdf.ValueTypeNames.Token
        ).ConnectToSource(shader_output)

    # Save the stage
    stage.Save()
    
    return [modified_files, created_files]

def add_sublayers(args, file_list) -> list:
    modified_files = []
    game_ready_assets_path = os.path.join(args.directory)
    mod_file_path = os.path.join(game_ready_assets_path, "mod.usda")
    if os.path.exists(mod_file_path):
        modified_files.append(mod_file_path)

        # Open the existing stage
        stage = Usd.Stage.Open(mod_file_path)

        # Get the existing sublayers
        existing_sublayers = list(stage.GetRootLayer().subLayerPaths)

        # Create a set of existing sublayer file names
        existing_sublayer_files = {
            os.path.basename(sublayer_path) for sublayer_path in existing_sublayers
        }

        # Add new sublayers
        new_sublayers = [
            f"./{args.output}{suffix}.usda"
            for suffix in suffixes
                if  f"{args.output}{suffix}.usda" not in existing_sublayer_files
                and f"{args.output}{suffix}.usda" in     file_list
        ]
        stage.GetRootLayer().subLayerPaths = (existing_sublayers + new_sublayers)

        # Save the stage
        stage.Save()

    return modified_files

if __name__ == "__main__":
    ## ARGUMENT BLOCK
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", required=True, help="Path to directory")
    parser.add_argument("-o", "--output", default="mod", help="Output file name")
    parser.add_argument("-e", "--exclude-non-hashes", action="store_true", help="Exclude any files without a hash from being included in the output .usda file")
    parser.add_argument("-g", "--generate-hashes", action="store_true", help="Generates hashes for file names before the suffix")
    parser.add_argument("-m", "--multiple-files", action="store_true", help="Save multiple .usda files, one for each suffix type (except for diffuse)")
    parser.add_argument("-a", "--add-sublayers", action="store_true", help="Add sublayers made with -m to the mod.usda file. This argument only modifies the mod.usda file and does not affect any custom USDA file specified by the -o argument.")
    parser.add_argument("-r", "--reference-directory", help="Path to reference directory for diffuse texture hashes")
    args = parser.parse_args()
     
    # Check target processing directory before use
    if not os.path.isdir(args.directory):
        raise FileNotFoundError("Specified processing directory (-d) is invalid")
    
    file_list = os.listdir(os.path.join(args.directory))
    created_files  = []
    modified_files = []
    
    # Process sublayer additions
    if args.add_sublayers:
        modified_files.extend(add_sublayers(args, file_list))
    
    # Generate unique USDA files per suffix type (except diffuse)
    if args.multiple_files:
        for suffix in suffixes:
            m, c = write_usda_file(args, file_list, suffix)
            modified_files.extend(m), created_files.extend(c)
    else:  # Generate a single USDA file for all suffixes
        m, c = write_usda_file(args, file_list)
        modified_files.extend(m), created_files.extend(c)
    
    # Complete
    print("Finished!")
    print("Created files:")
    for file in created_files:
        print(f"  - {file}")
    print("Modified files:")
    for file in modified_files:
        print(f"  - {file}")
