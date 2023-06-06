import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory', help='Path to your gameReadyAssets directory. Do not use any other directory!', required=True)
args = parser.parse_args()

directory_path = args.directory
game_ready_assets_path = os.path.join(directory_path)

hashes = set()
suffixes = ['_normal', '_emissive', '_metallic', '_rough']

for file_name in os.listdir(game_ready_assets_path):
    if file_name.endswith('.dds'):
        if '_' not in file_name:
            hashes.add(file_name[:-4])
        else:
            name, suffix = file_name.rsplit('_', 1)
            if suffix in suffixes:
                hashes.add(name)

usda_file_name = 'mod.usda'
usda_file_path = os.path.join(game_ready_assets_path, usda_file_name)
with open(usda_file_path, 'w') as usda_file:
    usda_file.write(f'''#usda 1.0
(
    upAxis = "Y"
)

def Scope "Looks"
{{
}}

over "RootNode"
{{
    over "Looks"
    {{''')
    
    for hash in hashes:
        usda_file.write(f'''
        over "mat_{hash}"
        {{
            over "Shader"
            {{''')
        
        if f'{hash}.dds' in os.listdir(game_ready_assets_path):
            usda_file.write(f'''
                asset inputs:diffuse_texture = @./{hash}.dds@ (
                    customData = {{
                        asset default = @@
                    }}
                    displayGroup = "Diffuse"
                    displayName = "Albedo Map"
                    doc = "The texture specifying the albedo value and the optional opacity value to use in the alpha channel"
                    hidden = false
                )''')
        
        if f'{hash}_emissive.dds' in os.listdir(game_ready_assets_path):
            usda_file.write(f'''
                asset inputs:emissive_mask_texture = @./{hash}_emissive.dds@ (
                    colorSpace = "auto"
                    customData = {{
                        asset default = @@
                    }}
                    displayGroup = "Emissive"
                    displayName = "Emissive Mask Map"
                    doc = "The texture masking the emissive color"
                    hidden = false
                )
                bool inputs:enable_emission = 1 (
                    customData = {{
                        bool default = 0
                    }}
                    displayGroup = "Emissive"
                    displayName = "Enable Emission"
                    doc = "Enables the emission of light from the material"
                    hidden = false
                )
                float inputs:emissive_intensity = 5 (
                    customData = {{
                        float default = 40
                        dictionary range = {{
                            float max = 65504
                            float min = 0
                        }}
                    }}
                    displayGroup = "Emissive"
                    displayName = "Emissive Intensity"
                    doc = "Intensity of the emission"
                    hidden = false
                )''')
        
        usda_file.write('''
                int inputs:encoding = 0''')
        
        if f'{hash}_metallic.dds' in os.listdir(game_ready_assets_path):
            usda_file.write(f'''
                asset inputs:metallic_texture = @./{hash}_metallic.dds@ (
                    colorSpace = "auto"
                    customData = {{
                        asset default = @@
                    }}
                    displayGroup = "Specular"
                    displayName = "Metallic Map"
                    hidden = false
                )''')
        
        if f'{hash}_normal.dds' in os.listdir(game_ready_assets_path):
            usda_file.write(f'''
                asset inputs:normalmap_texture = @./{hash}_normal.dds@''')
        
        if f'{hash}_rough.dds' in os.listdir(game_ready_assets_path):
            usda_file.write(f'''
                asset inputs:reflectionroughness_texture = @./{hash}_rough.dds@ (
                    colorSpace = "auto"
                    customData = {{
                        asset default = @@
                    }}
                    displayGroup = "Specular"
                    displayName = "Roughness Map"
                    hidden = false
                )''')
        
        usda_file.write('''
            }
        }''')
    
    usda_file.write('''
    }
}
''')
