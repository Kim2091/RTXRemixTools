import argparse
import logging
import os
import sys

from pxr import Usd, UsdGeom, Gf, Sdf

ALIASES = {
    "primvars:UVMap": ("primvars:st", Sdf.ValueTypeNames.Float2Array),
    "primvars:UVChannel_1": ("primvars:st1", Sdf.ValueTypeNames.Float2Array),
    "primvars:map1": ("primvars:st1", Sdf.ValueTypeNames.Float2Array),
    # Add more aliases here
}


def convert_face_varying_to_vertex_interpolation(usd_file_path):
    stage = Usd.Stage.Open(usd_file_path)
    mesh_prims = [prim for prim in stage.TraverseAll() if prim.IsA(UsdGeom.Mesh)]
    for prim in mesh_prims:
        mesh = UsdGeom.Mesh(prim)
        indices = prim.GetAttribute("faceVertexIndices")
        points = prim.GetAttribute("points")
        
        if not indices or not points:
            continue  # Skip if the required attributes are missing
        
        points_arr = points.Get()

        modified_points = [points_arr[i] for i in indices.Get()]
        points.Set(modified_points)

        indices.Set([i for i in range(len(indices.Get()))])

        mesh.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
        primvar_api = UsdGeom.PrimvarsAPI(prim)
        for var in primvar_api.GetPrimvars():
            if var.GetInterpolation() == UsdGeom.Tokens.faceVarying:
                var.SetInterpolation(UsdGeom.Tokens.vertex)

            # Replace aliases with "float2[] primvars:st"
            if var.GetName() in ALIASES:
                new_name, new_type_name = ALIASES[var.GetName()]
                new_var = primvar_api.GetPrimvar(new_name)
                if new_var:
                    new_var.Set(var.Get())
                else:
                    new_var = primvar_api.CreatePrimvar(new_name, new_type_name)
                    new_var.Set(var.Get())
                    new_var.SetInterpolation(UsdGeom.Tokens.vertex) # Set interpolation to vertex
                
                primvar_api.RemovePrimvar(var.GetBaseName())

    return stage

def convert_file_format(input_file, output_file):
    stage = Usd.Stage.Open(input_file)
    stage.Export(output_file)
    logging.info(f"File format conversion performed: {input_file} -> {output_file}")
    return stage


def process_folder(input_folder, output_folder, output_format):
    for file_name in os.listdir(input_folder):
        input_file = os.path.join(input_folder, file_name)
        output_file = os.path.join(output_folder, os.path.splitext(file_name)[0] + '.' + output_format)

        if not os.path.isfile(input_file):
            continue

        stage = convert_face_varying_to_vertex_interpolation(input_file)

        if output_file.endswith(".usd") or output_file.endswith(".usda"):
            stage = convert_file_format(input_file, output_file)
            stage.Export(output_file)  # Export again using the output file path


def main():
    parser = argparse.ArgumentParser(description='Convert USD file formats and interpolation of meshes.')
    parser.add_argument('input', type=str, help='Input file or folder path')
    parser.add_argument('output', type=str, help='Output file or folder path')
    parser.add_argument('-f', '--output-format', type=str, choices=['usd', 'usda'], help='Output format when processing a folder')
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    output_format = args.output_format

    logging.basicConfig(level=logging.INFO, format='%(message)s')

    if os.path.isdir(input_path):
        process_folder(input_path, output_path, output_format)
    else:
        stage = convert_face_varying_to_vertex_interpolation(input_path)

        if output_path.endswith(".usd") or output_path.endswith(".usda"):
            stage = convert_file_format(input_path, output_path)
            stage.Export(output_path)  # Export again using the output file path


if __name__ == '__main__':
    main()
