#!/usr/bin/env python3

import PIL.Image
import PIL.ImageDraw
import functools
import json
import os.path
import pathlib

with (pathlib.Path(__file__).resolve().parent / 'config.json').open() as config_f:
    CONFIG = json.load(config_f)

target_dir = pathlib.Path(__file__).resolve().parent / 'simplify'
TRANSPARENT = (0, 0, 0, 0)

class Palette:
    def __init__(self, palette_data):
        if isinstance(palette_data, Palette):
            # copy other palette
            self.base = palette_data.base
            self.highlight = palette_data.highlight
            self.shadow = palette_data.shadow
        elif isinstance(palette_data, dict):
            # from parsed JSON
            self.base = self.decode_color(palette_data['base'])
            self.highlight = self.decode_color(palette_data['highlight'])
            self.shadow = self.decode_color(palette_data['shadow'])
        elif isinstance(palette_data, str):
            # from config.json
            self.base = CONFIG['palette'][palette_data]['base']
            self.highlight = CONFIG['palette'][palette_data]['highlight']
            self.shadow = CONFIG['palette'][palette_data]['shadow']
        elif isinstance(palette_data, tuple):
            # single-color palette
            self.base = self.highlight = self.shadow = palette_data
        else:
            raise NotImplementedError('Cannot create palette from data of type {}'.format(palette_data.__class__.__name__))

    @staticmethod
    def decode_color(color):
        if isinstance(color, list):
            return tuple(color)
        elif isinstance(color, str):
            return color
        elif isinstance(color, tuple):
            return color
        else:
            raise NotImplementedError('Cannot create color from data of type {}'.format(color.__class__.__name__))

    @property
    def inverted(self):
        return Palette({
            'base': self.base,
            'highlight': self.shadow,
            'shadow': self.highlight
        })

class Texture:
    def __init__(self, color=TRANSPARENT):
        self.image = PIL.Image.new('RGBA', (16, 16), color=color)

    @classmethod
    def from_image(cls, image):
        ret = cls()
        ret.image = image
        return ret

    def brick(self, palette):
        return self.square(palette, bounds=(0, 0, 16, 8)).square(palette, bounds=(8, 8, 17, 16)).square(palette, bounds=(-1, 8, 8, 16))

    def brick_ore(self, palette):
        return self.square(palette, bounds=(2, 2, 6, 5)).square(palette, bounds=(9, 3, 13, 6)).square(palette, bounds=(10, 10, 14, 13)).square(palette, bounds=(1, 11, 5, 14))

    def ore(self, palette):
        return self.square(palette, bounds=(2, 3, 7, 7)).square(palette, bounds=(9, 3, 13, 6)).square(palette, bounds=(3, 9, 8, 14)).square(palette, bounds=(10, 7, 14, 11))

    def save(self, path):
        save_image(path, self.image)

    def square(self, palette, bounds=(0, 0, 16, 16)):
        new_layer = PIL.Image.new('RGBA', (16, 16), color=TRANSPARENT)
        draw = PIL.ImageDraw.Draw(new_layer)
        # the highlight along the upper and left edges
        draw.line([(bounds[0], bounds[1]), (bounds[0], bounds[3] - 2)], fill=palette.highlight)
        draw.line([(bounds[0] + 1, bounds[1]), (bounds[2] - 2, bounds[1])], fill=palette.highlight)
        # the shadow along the lower and right edges
        draw.line([(bounds[0] + 1, bounds[3] - 1), (bounds[2] - 1, bounds[3] - 1)], fill=palette.shadow)
        draw.line([(bounds[2] - 1, bounds[1] + 1), (bounds[2] - 1, bounds[3] - 2)], fill=palette.shadow)
        # the rest of the square
        if bounds[2] - bounds[0] > 2 and bounds[3] - bounds[1] > 2:
            draw.rectangle([(bounds[0] + 1, bounds[1] + 1), (bounds[2] - 2, bounds[3] - 2)], fill=palette.base)
        draw.point((bounds[0], bounds[3] - 1), fill=palette.base)
        draw.point((bounds[2] - 1, bounds[1]), fill=palette.base)
        return self.__class__.from_image(PIL.Image.alpha_composite(self.image, new_layer))

    def stripes(self, palette):
        return self.square(palette, bounds=(2, 3, 14, 5)).square(palette, bounds=(2, 7, 14, 9)).square(palette, bounds=(2, 11, 14, 13))

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
    @functools.wraps(f)
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
    data.save(path)

@normalize_path
def save_json(path, data):
    with path.open('w') as open_file:
        json.dump(data, open_file, indent=4, sort_keys=True)

def simplify_textures(path=['textures']):
    config = CONFIG
    directory = target_dir / 'assets' / 'minecraft'
    for path_segment in path:
        config = config[path_segment]
        directory /= path_segment
    for name, item in config.items():
        if name.endswith('.png'):
            # texture
            texture = Texture()
            for layer in item['layers']:
                palette = Palette(layer['palette'])
                if layer.get('inverted', False):
                    palette = palette.inverted
                texture = {
                    'brick': texture.brick,
                    'brickOre': texture.brick_ore,
                    'ore': texture.ore,
                    'square': texture.square,
                    'stripes': texture.stripes
                }[layer['shape']](palette)
            texture.save(directory / name)
        else:
            # subdirectory
            simplify_textures(path=path + [name])

def simplify():
    clear_target()
    save_json('pack.mcmeta', {
        'pack': {
            'description': "Simplify - a texture pack by Fenhl",
            'pack_format': 1
        }
    })
    simplify_textures()
    #TODO others

if __name__ == '__main__':
    simplify()
