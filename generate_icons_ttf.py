#!/usr/bin/fontforge

import fontforge
import optparse
import json
import os

STYLES = ('regular', 'filled')
ASSETS = sorted([x for x in os.listdir("assets") if x != '.DS_Store'])

CONFIG_FILE = os.path.splitext(__file__)[0] + '.json'
DATA = {}

NEXT_CODEPOINT = 0xe000

def get_mapped_codepoint(name):
    global NEXT_CODEPOINT

    glyph_map = DATA['glyph_map']

    item = next(filter(lambda x: x[1] == name, glyph_map.items()), None)
    if not item is None:
        return int(item[0], 16)

    while hex(NEXT_CODEPOINT) in glyph_map:
        NEXT_CODEPOINT += 1
    codepoint = NEXT_CODEPOINT
    NEXT_CODEPOINT += 1

    glyph_map[hex(codepoint)] = name
    return codepoint

def get_weigths(style):
    weights = set()
    for asset in ASSETS:
        svg_dir = os.path.join("assets", asset, "SVG")
        for filename in sorted(os.listdir(svg_dir)):
            weight = int(filename.split("_")[-2])
            weights.add(weight)
    return sorted(list(weights))

def get_weigths_for_asset(style, asset):
    weights = []
    svg_dir = os.path.join("assets", asset, "SVG")
    for filename in sorted(os.listdir(svg_dir)):
        if style == filename.split("_")[-1].replace(".svg", ""):
            weight = int(filename.split("_")[-2])
            weights += [weight]
    return sorted(weights)

def array_get(array, index, default=None):
    if index < len(array):
        return array[index]
    else:
        return default

def main():
    parser = optparse.OptionParser()
    parser.add_option("-s", dest="style",
                      help="set the icon style to generate " + str(STYLES),
                      metavar="style", default="regular")
    parser.add_option("-w", dest="weight", type="int",
                      help="set the weight to generate",
                      metavar="weight", default=20)
    parser.add_option("-o", dest="output",
                      help="set the output file",
                      metavar="output")
    parser.add_option("-n", dest="name",
                      help="set the font name",
                      metavar="name")

    (options, args) = parser.parse_args()

    style = options.style
    weight = options.weight
    output = options.output
    name = options.name

    if output is None:
        output = 'fluentui-system-%s-%d.ttf' % (style, weight)
    if name is None:
        name = 'Fluent System %s W%d' % (style.capitalize(), weight)

    ###
    sys.stderr.write('* Font name: %s\n' % (name))
    sys.stderr.write('* Font style: %s\n' % (style))
    sys.stderr.write('* Font weight: %s\n' % (weight))
    sys.stderr.write('* Output to: %s\n' % (output))

    ###
    if not style in STYLES:
        sys.stderr.write('The font style "%s" does not exist.\n' % (style))
        sys.exit(1)

    ###
    global DATA
    if os.path.exists(CONFIG_FILE):
        DATA = json.load(open(CONFIG_FILE))

    glyph_map = DATA.setdefault('glyph_map', {})

    font = fontforge.font()
    font.familyname = name
    font.descent = 0

    for asset in ASSETS:
        unicode = get_mapped_codepoint(asset)

        selected_weight = None
        selected_file = None

        asset_weights = get_weigths_for_asset(style, asset)
        fitting_weights = list(filter(lambda w: w <= weight, asset_weights))
        if len(fitting_weights) > 0:
            selected_weight = fitting_weights[-1]
        elif len(asset_weights) > 0:
            selected_weight = asset_weights[0]

        if selected_weight != None:
            svg_dir = os.path.join("assets", asset, "SVG")
            for filename in sorted(os.listdir(svg_dir)):
                asset_style = filename.split("_")[-1].replace(".svg", "")
                asset_weight = int(filename.split("_")[-2])
                if (style == asset_style) and (selected_weight == asset_weight):
                    selected_file = os.path.join(svg_dir, filename)
                    break

        if not (selected_file is None):
            glyph = font.createChar(unicode)
            glyph.importOutlines(selected_file)
            glyph.width = 800
            glyph.vwidth = 800

    # font.save('fluentui-system-%s-%d.sfd' % (style, weight))
    font.generate(output)

    json.dump(DATA, open(CONFIG_FILE, 'w'), indent=True)

if __name__ == '__main__':
    main()
