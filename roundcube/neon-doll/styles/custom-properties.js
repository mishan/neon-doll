/**
 * Neon Doll for Roundcube: a lessc plugin that lets LESS's color functions
 * take a custom property.
 *
 * Elastic derives colors with darken(), fade() and the like, and LESS
 * evaluates every variable, even one a skin redefines, so a var(--nd-...)
 * anywhere upstream of them is an error. With this, a function handed a
 * custom property (or anything else that isn't a color) writes the CSS
 * color-mix() that does the same thing in the browser, and a real color is
 * left to LESS as before.
 */

module.exports = {
    install(less, pluginManager, functions) {
        const { Color, Anonymous, Dimension } = less.tree;
        const css = (node) => node.toCSS({});
        const pct = (amount) => {
            const v = amount instanceof Dimension ? amount.value : parseFloat(css(amount));
            return (amount.unit && amount.unit.is('%')) || v > 1 ? v : v * 100;
        };
        const mix = (a, weight, b) =>
            new Anonymous(`color-mix(in srgb, ${a} ${weight}%, ${b})`);

        const fallbacks = {
            darken: (c, p) => mix(css(c), 100 - pct(p), 'black'),
            lighten: (c, p) => mix(css(c), 100 - pct(p), 'white'),
            shade: (c, p) => mix(css(c), 100 - pct(p), 'black'),
            tint: (c, p) => mix(css(c), 100 - pct(p), 'white'),
            fade: (c, p) => mix(css(c), pct(p), 'transparent'),
            fadeout: (c, p) => mix(css(c), 100 - pct(p), 'transparent'),
            fadein: (c) => c,
            saturate: (c) => c,
            desaturate: (c) => c,
            spin: (c) => c,
            mix: (a, b, w) => mix(css(a), w ? pct(w) : 50, css(b)),
        };

        for (const [name, fallback] of Object.entries(fallbacks)) {
            const builtin = less.functions.functionRegistry.get(name);
            functions.add(name, function (...args) {
                const colors = name === 'mix' ? args.slice(0, 2) : args.slice(0, 1);
                if (colors.every((c) => c instanceof Color)) {
                    return builtin.apply(this, args);
                }
                return fallback(...args);
            });
        }
    },
};
