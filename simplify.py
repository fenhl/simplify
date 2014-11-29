#!/usr/bin/env python3

import PIL.Image
import json
import os.path
import pathlib

target_dir = pathlib.Path(__file__).resolve().parent / 'simplify'

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
    stone = PIL.Image.new('RGBA', (16, 16), color=(0x80, 0x80, 0x80, 0xff))
    for x, y in iter_image(stone):
        if x == 0 and y < 15 or y == 0 and x < 15:
            stone.putpixel((x, y), (0xa3, 0xa3, 0xa3, 0xff))
        elif x == 15 and y > 0 or y == 15 and x > 0:
            stone.putpixel((x, y), (0x5f, 0x5f, 0x5f, 0xff))
    save('assets/minecraft/textures/blocks/stone.png', stone)
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
