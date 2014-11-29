#!/usr/bin/env python3

import PIL.Image
import PIL.ImageDraw
import json
import os.path
import pathlib

target_dir = pathlib.Path(__file__).resolve().parent / 'simplify'
transparent = (0, 0, 0, 0)

palette = {
    'diamond': {
        'color': '#80ffff',
        'highlight_color': '#b0ffff',
        'shadow_color': '#00ffff'
    },
    'stone': {
        'color': '#808080',
        'highlight_color': '#a3a3a3',
        'shadow_color': '#5f5f5f'
    }
}

class Texture:
    def __init__(self, color=transparent):
        self.image = PIL.Image.new('RGBA', (16, 16), color=color)
    
    @classmethod
    def from_image(cls, image):
        ret = cls()
        ret.image = image
        return ret
    
    def brick(self, **colors):
        return self.square(bounds=(0, 0, 16, 8), **colors).square(bounds=(8, 8, 17, 16), **colors).square(bounds=(-1, 8, 8, 16), **colors)
    
    def ore(self, **colors):
        return self.square(bounds=(2, 3, 7, 7), **colors).square(bounds=(9, 3, 13, 6), **colors).square(bounds=(3, 9, 8, 14), **colors).square(bounds=(10, 7, 14, 11), **colors)
    
    def save(self, path):
        save_image(path, self.image)
    
    def square(self, color=transparent, highlight_color=transparent, shadow_color=transparent, bounds=(0, 0, 16, 16)):
        new_layer = PIL.Image.new('RGBA', (16, 16), color=transparent)
        draw = PIL.ImageDraw.Draw(new_layer)
        # the highlight along the upper and left edges
        draw.line([(bounds[0], bounds[1]), (bounds[0], bounds[3] - 2)], fill=highlight_color)
        draw.line([(bounds[0] + 1, bounds[1]), (bounds[2] - 2, bounds[1])], fill=highlight_color)
        # the shadow along the lower and right edges
        draw.line([(bounds[0] + 1, bounds[3] - 1), (bounds[2] - 1, bounds[3] - 1)], fill=shadow_color)
        draw.line([(bounds[2] - 1, bounds[1] + 1), (bounds[2] - 1, bounds[3] - 2)], fill=shadow_color)
        # the rest of the square
        draw.rectangle([(bounds[0] + 1, bounds[1] + 1), (bounds[2] - 2, bounds[3] - 2)], fill=color)
        draw.point((bounds[0], bounds[3] - 1), fill=color)
        draw.point((bounds[2] - 1, bounds[1]), fill=color)
        return self.__class__.from_image(PIL.Image.alpha_composite(self.image, new_layer))

def clear_target():
    def recursive_remove(path):
        if path.is_dir():
            for child in path.iterdir():
                recursive_remove(child)
            path.rmdir()
        else:
            path.unlink()
    
    if target_dir.exists():
        recursive_remove(target_dir)

def iter_image(img):
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            yield x, y

def normalize_path(f):
    def normalized_f(path, *args, **kwargs):
        path = target_dir / path
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        return f(path, *args, **kwargs)
    
    return normalized_f

@normalize_path
def save(path, data):
    if isinstance(data, PIL.Image.Image):
        save_image(path, data)
    elif isinstance(data, dict):
        save_json(path, data)
    else:
        raise NotImplementedError('saving not implemented for {!r}'.format(type(data)))

@normalize_path
def save_image(path, data):
    with path.open('wb') as open_file:
        data.save(open_file)

@normalize_path
def save_json(path, data):
    with path.open('w') as open_file:
        json.dump(data, open_file, indent=4, sort_keys=True)

def simplify_blocks():
    blocks = target_dir / 'assets/minecraft/textures/blocks'
    # stone
    stone = Texture().square(**palette['stone'])
    stone.save(blocks / 'stone.png')
    stone.ore(**palette['diamond']).save(blocks / 'diamond_ore.png')
    stone.ore(**palette['stone']).save(blocks / 'cobblestone.png')
    # stone bricks
    Texture().brick(**palette['stone']).save(blocks / 'stonebrick.png')
    # diamond
    Texture().square(**palette['diamond']).save(blocks / 'diamond_block.png')
    #TODO others

def simplify():
    clear_target()
    save_json('pack.mcmeta', {
        'pack': {
            'description': "Simplify - a texture pack by Fenhl",
            'pack_format': 1
        }
    })
    simplify_blocks()
    #TODO others

if __name__ == '__main__':
    simplify()
