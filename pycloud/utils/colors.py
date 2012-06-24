
"""
Rather than using any of:
http://pypi.python.org/pypi/pycolors2/0.0.2
http://packages.python.org/pycolors/

using:
https://raw.github.com/fabric/fabric/master/fabric/colors.py

#1 to keep colors output independent of another mdoule
#2 the fabric colors implementation is very close to the pycolors2
implementation, just a little smaller


Functions for wrapping strings in ANSI color codes.

Each function within this module returns the input string ``text``, wrapped
with ANSI color codes for the appropriate color.

For example, to print some text as green on supporting terminals::

    from fabric.colors import green

    print(green("This text is green!"))

Because these functions simply return modified strings, you can nest them::

    from fabric.colors import red, green

    print(red("This sentence is red, except for " + \
          green("these words, which are green") + "."))

If ``bold`` is set to ``True``, the ANSI flag for bolding will be flipped on
for that particular invocation, which usually shows up as a bold or brighter
version of the original color on most terminals.
"""


def _wrap_with(code):

    def inner(text, bold=False):
        c = code
        if bold:
            c = "1;%s" % c
        return "\033[%sm%s\033[0m" % (c, text)
    return inner

red = _wrap_with('31')
green = _wrap_with('32')
yellow = _wrap_with('33')
blue = _wrap_with('34')
magenta = _wrap_with('35')
cyan = _wrap_with('36')
white = _wrap_with('37')
