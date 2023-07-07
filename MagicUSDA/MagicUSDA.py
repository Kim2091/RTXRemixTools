import os
import argparse
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
    created_files = []
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
            # Extract only the file name from the absolute path
            name = os.path.basename(file_name)
            name, ext = os.path.splitext(name)
            if "_" not in name or name.endswith("_diffuse"):
                # Check if the generate_hashes argument is specified
                if args.generate_hashes:
                    key = generate_hashes(os.path.join(reference_directory, file_name))
                else:
                    key = os.path.basename(name)
                    # Check if the key contains a hash
                    if not (key.isupper() and len(key) == 16):
                        continue
                # Remove the _diffuse suffix from the key
                key = key.replace("_diffuse", "")
                # Get the relative path from the game ready assets path to the texture file
                rel_file_path = os.path.relpath(file_name, args.directory)
                targets[key] = rel_file_path

    # Create a new stage
    stage = Usd.Stage.CreateNew(usda_file_path)

    # Modify the existing RootNode prim
    root_node_prim = stage.OverridePrim("/RootNode")

    # Add a Looks scope as a child of the RootNode prim
    looks_scope = UsdGeom.Scope.Define(stage, "/RootNode/Looks")
    
    added_targets = set()
    for value, name in targets.items():
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
            # Use the dynamically generated relative path for the diffuse texture
            diffuse_texture.Set(f".\{rel_file_path}")
        
        # Process each type of texture
        if not suffix or suffix == "_emissive":
            emissive_file_name = f"{value}_emissive.dds"
            print(f"Emissive File Name: {emissive_file_name in file_list}")
            # print(file_list)
            if any(file_path.endswith(emissive_file_name) for file_path in file_list):
                emissive_mask_texture = shader_prim.CreateInput(
                    "emissive_mask_texture", Sdf.ValueTypeNames.Asset
                )
                # Use the dynamically generated relative path for the emissive texture
                emissive_rel_file_path = os.path.relpath(os.path.join(game_ready_assets_path, emissive_file_name), args.directory)
                emissive_mask_texture.Set(f".\{emissive_rel_file_path}")
                enable_emission = shader_prim.CreateInput(
                    "enable_emission", Sdf.ValueTypeNames.Bool
                )
                enable_emission.Set(True)
                emissive_intensity = shader_prim.CreateInput(
                    "emissive_intensity", Sdf.ValueTypeNames.Float
                )
                emissive_intensity.Set(5)

        if not suffix or suffix == "_metallic":
            metallic_file_name = f"{value}_metallic.dds"
            if any(file_path.endswith(metallic_file_name) for file_path in file_list):

                metallic_texture = shader_prim.CreateInput(
                    "metallic_texture", Sdf.ValueTypeNames.Asset
                )
                # Use the dynamically generated relative path for the metallic texture
                metallic_rel_file_path = os.path.relpath(os.path.join(game_ready_assets_path, metallic_file_name), args.directory)
                metallic_texture.Set(f".\{metallic_rel_file_path}")

        if not suffix or suffix == "_normal":
            normal_file_name = f"{value}_normal.dds"
            if any(file_path.endswith(normal_file_name) for file_path in file_list):
                normalmap_texture = shader_prim.CreateInput(
                    "normal_texture", Sdf.ValueTypeNames.Asset
                )
                # Use the dynamically generated relative path for the normal texture
                normal_rel_file_path = os.path.relpath(os.path.join(game_ready_assets_path, normal_file_name), args.directory)
                normalmap_texture.Set(f".\{normal_rel_file_path}")

        if not suffix or suffix == "_rough":
            roughness_file_name = f"{value}_rough.dds"
            if any(file_path.endswith(roughness_file_name) for file_path in file_list):
                reflectionroughness_texture = shader_prim.CreateInput(
                    "roughness_texture", Sdf.ValueTypeNames.Asset
                )
                # Use the dynamically generated relative path for the roughness texture
                roughness_rel_file_path = os.path.relpath(os.path.join(game_ready_assets_path, roughness_file_name), args.directory)
                reflectionroughness_texture.Set(f".\{roughness_rel_file_path}")

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
            if f"{args.output}{suffix}.usda" not in existing_sublayer_files
            and any(
                os.path.basename(file_path) == f"{args.output}{suffix}.usda"
                for file_path in file_list
            )
        ]
        stage.GetRootLayer().subLayerPaths = (existing_sublayers + new_sublayers)

        # Save the stage
        stage.Save()

    return modified_files


if __name__ == "__main__":
    # ARGUMENT BLOCK
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", required=True, help="Path to directory")
    parser.add_argument("-o", "--output", default="mod", help="Output file name")
    parser.add_argument("-g", "--generate-hashes", action="store_true", help="Generates hashes for file names before the suffix")
    parser.add_argument("-m", "--multiple-files", action="store_true", help="Save multiple .usda files, one for each suffix type (except for diffuse)")
    parser.add_argument("-a", "--add-sublayers", action="store_true", help="Add sublayers made with -m to the mod.usda file. This argument only modifies the mod.usda file and does not affect any custom USDA file specified by the -o argument.")
    parser.add_argument("-r", "--reference-directory", help="Path to reference directory for diffuse texture hashes")
    args = parser.parse_args()
     
    # Check target processing directory before use
    if not os.path.isdir(args.directory):
        raise FileNotFoundError("Specified processing directory (-d) is invalid")
    
    # Recursively scan folders
    file_list = []
    for root, dirs, files in os.walk(args.directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    created_files  = []
    modified_files = []
    
    # Process sublayer additions
    print(f"Add Sublayers: {args.add_sublayers}")
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
