**Simplify** is a resource pack for [Minecraft][] containing textures and other graphical resources (a texture pack). It is a “simple” pack (thus the name), featuring basic recurring shapes and color palettes, and shaded edges to help tell adjacent blocks apart. While textures may appear similar to those in other texture packs, they were created by Fenhl, using only the default textures as a starting point.

This repository contains the source code for the resource pack. See the sections below for the actual pack.

This texture pack should update whenever Minecraft updates, so if it lacks textures from the latest Minecraft release, feel free to submit an issue.

There are some [screenshots][].

Download
========

You can download Simplify as a zip from the [releases][] page. Releases are namef after their corresponding Minecraft version.

Snapshots and pre-releases
==========================

If you're on a version of Minecraft for which no release is available, you can generate Simplify yourself. In a shell, run the following commands:

```shellsession
$ git clone https://github.com/fenhl/simplify.git
$ cd simplify
$ git checkout dev
$ python3 simplify.py
```

The resource pack will be generated in the `simplify` directory within the cloned repo (`simplify/simplify` from where your shell session started).

[Minecraft]: http://minecraft.net/ (Minecraft)
[releases]: https://github.com/fenhl/simplify/releases (GitHub: fenhl: simplify: releases)
[screenshots]: http://fenhl.net/mc/simplify.php (Fenhl: Simplify: Screenshots)
