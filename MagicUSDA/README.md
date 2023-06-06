## Remix USDA Generator
*Written with the assistance of Bing*

This is a script to generate `.usda` files from your gameReadyAssets folder. It detects any of these map types in your folder:
- emissive
- normal
- metallic
- rough

It then generates a corresponding `mod.usda` file for you to use in your game. This is intended to be used with a chaiNNer chain that generates these files from a captured game texture.

The purpose of these `.usda` files is to replace textures in your Remix games. This allows you to replace textures and also use the map types listed above to enhance the way the game looks.

How to use this script:
`python MagicUSDA.py -d path\to\gameReadyAssets`

It outputs a mod.usda file in the directory you specified. **It will overwrite any existing mod.usda file!**
