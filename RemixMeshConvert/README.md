## RemixMeshConvert
$\color{#f7d26a}{\textsf{Use this instead. It integrates directly into Omniverse:}}$ https://github.com/Ekozmaster/NvidiaOmniverseRTXRemixTools





<details>
  <summary>Old description:</summary>
  
*Based on a script originally written by E-man*

$\color{#f7d26a}{\textsf{Please back up your USD and USDA files before running!}}$

**How to use this script:**

To convert a single file:

`python RemixMeshConvert.py [input.usda] [output.usda]`

To batch convert a folder:

`python RemixMeshConvert.py path\to\input\folder path\to\output\folder -f [usd or usda]`

**Arguments:**

`-f` `--output-format` - This controls the output format when using the script in **batch** mode

**Description:**

This script takes USD files as input, makes a copy named as the output, converts the interpolation of all meshes in the given USD file from face-varying to vertex, and finally saves the modified stages to the new USD files. It can process a single file or a folder of files, and also includes a dictionary of aliases for replacing specific primvar names with `float2[] primvars:st1`.

**For your final exports to use in-game, please save as USD! USDA files are very inefficient in comparison**

Please refer to `requirements.txt` for necessary Python libraries.
</details>
