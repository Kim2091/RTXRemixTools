## faceVarying to Vertex
*Originally written by E-man*

$\color{#f7d26a}{\textsf{Please back up your usda files before running!}}$

**How to use this script:**

To convert a single file:

`python faceVarying_to_vertex.py [input.usda] [output.usda]`

To batch convert a folder:

`python faceVarying_to_vertex.py path\to\input\folder path\to\output\folder -f [usd or usda]`

**Arguments:**

`-f` `--output-format` - This controls the output format when using the script in **batch** mode

**Description:**

This script takes a USD file as input, converts the interpolation of all meshes in a USD file from face-varying to vertex, and exports the modified stage to a new USD file. This should help with mesh compatibility when using mesh exports from varous tools. It has been tested on Blender exports so far.
