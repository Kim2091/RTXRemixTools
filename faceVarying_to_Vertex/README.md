## faceVarying to Vertex
*Based on a script originally written by E-man*

$\color{#f7d26a}{\textsf{Please back up your usda files before running!}}$

**How to use this script:**

To convert a single file:

`python faceVarying_to_vertex.py [input.usda] [output.usda]`

To batch convert a folder:

`python faceVarying_to_vertex.py path\to\input\folder path\to\output\folder -f [usd or usda]`

**Arguments:**

`-f` `--output-format` - This controls the output format when using the script in **batch** mode

**Description:**

This script takes USD files as input, converts the interpolation of all meshes in the given USD file from face-varying to vertex, and exports the modified stage to new USD files. It can process a single file or a folder of files, and also includes a dictionary of aliases for replacing specific primvar names with `float2[] primvars:st1`.

Please refer to `requirements.txt` for necessary Python libraries.
