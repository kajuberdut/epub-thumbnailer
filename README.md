# What is UnCover?
UnCover is a fork of [epub-thumbnailer](https://github.com/marianosimone/epub-thumbnailer).

The goal of UnCover is to extract book covers from various file formats such as epub.

##Why fork?

The original project used a custom install script. To start wtih I only wanted to fork it to use the more conventional setup.py with an entry-point so that users could pip install easily. For fun I started making a few more changes and in the end only about 10% of code is shared with the upstream project.

Note that I don't have the original authors intent to support Gnome before version 3 or Python before version 3.6.

# How does it work?
It is strongly reccomended you use [pipx](https://github.com/pipxproject/pipx) to isolate the dependencies of uncover. This is also the easiest way to get up and running. If you don't have pipx installed follow [these instructions](https://github.com/pipxproject/pipx#install-pipx)

With pipx you can install UnCover with this command:

```
 pipx install --spec git+https://github.com/kajuberdut/uncover.git uncover
```

# Then what?

You can use UnCover in the command line like this:
```
uncover <epub_file> <output_file> --size 256
```

This will look into the **epub_file** to find its cover, and will save a **size** px png file as **output_file**

the --size flag is optional and defaults to 124 pixels.

# What about integration with Nautilus?

Nautilus, the file manager from Gnome, [supports custom thumbnailers](https://developer.gnome.org/integration-guide/stable/thumbnailer.html.en)

To register uncover with Nautilus just run:
```
uncover --register
```

To unregister you can run:
```
uncover --unregister
```

Both commands will likely ask you to enter your sudo password so they can create/remove a file in "/usr/share/thumbnailers". If you would rather not enter your password into that prompt they also provide a shell command you can copy and run seperately.

# Acknowledgments

- Particular thanks to [Mariano Simone](https://github.com/marianosimone) the author of the parent project
- Indirect thanks to all of Mariono's contributors:
    - [Marcelo Lira](https://github.com/setanta): Improved cover detection by filename
    - [Pablo Jorge](https://github.com/pablojorge): Added manifest-based cover detection
    - [Renato Ramonda](https://github.com/renatoram): Added gnome3 thumbnailer support
    - [xtrymind](https://github.com/xtrymind): Added tumbler configuration
    - A [couple](http://ubuntuforums.org/showthread.php?t=278162) of [forum](http://ubuntuforums.org/showthread.php?t=1046678)