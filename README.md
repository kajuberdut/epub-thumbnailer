# What is UnCover?
UnCover is a fork of [epub-thumbnailer](https://github.com/marianosimone/epub-thumbnailer).

The goal of UnCover is to extract book covers from various file formats such as epub.

# How does it work?
We strongly reccomend you use [pipx](https://github.com/pipxproject/pipx) to isolate the dependencies of uncover. This is also the easiest way to get up and running. If you don't have pipx installed follow [these instructions](https://github.com/pipxproject/pipx#install-pipx)

With pipx you can install UnCover with this command:

```
 pipx install --spec git+https://github.com/kajuberdut/epub-thumbnailer.git uncover
```

# Then what?

You can use UnCover in the command line like this:
```
uncover <epub_file> <output_file> --size 256
```

This will look into the **epub_file** to find its cover, and will save a **size** px png file as **output_file**

the --size flag is optional and defaults to 124 pixels.


# Acknowledgments

- Particular thanks to [Mariano Simone](https://github.com/marianosimone) the author of the parent project
- Indirect thanks to all of Mariono's contributors:
    - [Marcelo Lira](https://github.com/setanta): Improved cover detection by filename
    - [Pablo Jorge](https://github.com/pablojorge): Added manifest-based cover detection
    - [Renato Ramonda](https://github.com/renatoram): Added gnome3 thumbnailer support
    - [xtrymind](https://github.com/xtrymind): Added tumbler configuration
    - A [couple](http://ubuntuforums.org/showthread.php?t=278162) of [forum](http://ubuntuforums.org/showthread.php?t=1046678)