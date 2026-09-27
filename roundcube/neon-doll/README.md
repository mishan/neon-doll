Neon Doll for Roundcube
=======================

Hot pink neon on midnight plum, for Roundcube Webmail. A child of Elastic,
Roundcube's default skin: Elastic's layout, icons and scripts, in Neon
Doll's colors and shapes. Light and dark are both in it, and it follows
Roundcube's own switch (the Dark mode / Light mode button in the menu, which
follows the system until you press it).

Built against Roundcube 1.7.4, and tested on 1.7.4 and 1.6.18 (upstream's
release and Debian 13's package). Part of Neon Doll:
https://github.com/mishan/neon-doll


INSTALLATION
------------

Copy this folder into Roundcube's `skins/` folder, next to `elastic/`,
which it needs:

```
    $ cp -r neon-doll /path/to/roundcube/skins/
```

Then pick Neon Doll in Settings → Preferences → User Interface, or make it
everyone's default in `config/config.inc.php`:

```
    $config['skin'] = 'neon-doll';
```


BUILDING
--------

`styles/*.css` are compiled and ready. They come from `styles/*.less`,
which import Elastic's LESS and are compiled with this folder's `styles/`
on lessc's include path, where Elastic looks for a skin's `_variables.less`
and `_styles.less`. For a Roundcube other than 1.7, rebuild them against its
Elastic, from this folder inside `skins/`:

```
    $ for f in styles embed print; do
        npx -p less@4.9.1 lessc --rewrite-urls=all --include-path=styles \
          styles/$f.less > styles/$f.css
      done
```

In the Neon Doll repository, `tools/build-roundcube.py` does the same, and
writes `styles/_palette.less` and `watermark.html` from its `tokens.toml`.

`templates/includes/layout.html` is Elastic's, copied unchanged. It is the
template that links the stylesheet, and Roundcube looks for what an included
template links in that template's own skin first; with Elastic's copy, an
Elastic that has a `styles.css` of its own (Debian's does) would win over
this skin's. Copy it again from the same Elastic when you rebuild.


LICENSE
-------

Copyright (c) Misha Nasledov.

This skin's own files (the LESS, the plugin, meta.json, watermark.html and
the thumbnail) are yours to use under either of two licenses, your choice:

- the GNU General Public License, version 3 or later (COPYING, as in the
  rest of Neon Doll), or
- the Creative Commons Attribution-ShareAlike 4.0 International License
  (LICENSE-CC-BY-SA-4.0.txt, or
  https://creativecommons.org/licenses/by-sa/4.0/).

`templates/includes/layout.html` is Elastic's, under Elastic's license
below.

The compiled `styles/*.css` combine those files with Roundcube's Elastic
skin, by Aleksander Machniak and the Roundcube Dev Team, which is under the
Creative Commons Attribution-ShareAlike License 3.0
(http://creativecommons.org/licenses/by-sa/3.0/). They are an adaptation of
Elastic, and are licensed as a whole under CC BY-SA 4.0, as Elastic's
license allows for a later version with the same terms.

The skin uses Elastic's own files where they are installed, as they are:
Bootstrap, Font Awesome and the Roboto fonts, under their own licenses (see
skins/elastic/README.md).
