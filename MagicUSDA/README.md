## Remix USDA Generator
*Written with the assistance of Bing*

How to use this script:
`python MagicUSDA.py -d path\to\gameReadyAssets`
There are some additional functions:
* `-o` - This allows you to change the output usda file name
* `-g` - This enables hash generation for your texture names. The purpose of this one is to work with extracted game textures, where you can dump the textures right from the game files. This only works if the game textures are IDENTICAL to the ones Remix dumps

This is a script to generate `.usda` files from your gameReadyAssets folder. It detects any of these map types in your folder:
- emissive
- normal
- metallic
- rough

It then generates a corresponding `mod.usda` file for you to use in your game. This is intended to be used with [chaiNNer](https://chainner.app/) to generate these files from a captured game texture. **This script will overwrite any existing `mod.usda` files in your directory!**

The purpose of these `.usda` files is to replace textures in your Remix games. This allows you to replace textures and also use the map types listed above to enhance the way the game looks. 
