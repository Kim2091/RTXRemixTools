from pxr import Usd, UsdGeom, Sdf

ALIASES = {
    "primvars:UVMap": ("primvars:st", Sdf.ValueTypeNames.Float2Array),
    "primvars:UVChannel_1": ("primvars:st1", Sdf.ValueTypeNames.Float2Array),
    "primvars:map1": ("primvars:st1", Sdf.ValueTypeNames.Float2Array),
    # Add more aliases here
}

def convert_face_varying_to_vertex_interpolation(stage):
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
                
                # Remove the old primvar directly from the UsdGeomPrimvar object
                var.GetAttr().Block()

    return stage

stage = omni.usd.get_context().get_stage()
convert_face_varying_to_vertex_interpolation(stage)
