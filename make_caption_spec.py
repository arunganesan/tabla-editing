#! /usr/bin/env python
import json


ARRANGE_FILENAME = 'arrangement.json'
CAPTION_FILENAME = 'caption.json'
THEMES = json.load(open('library/themes.json'))
VARIATIONS = json.load(open('library/variations.json'))


def join_with_newline(bars):
    chunks = []
    PERLINE = 4
    for idx in range(0, len(bars), PERLINE):
        chunks.append(bars[idx:idx+PERLINE])
    line = '\n'.join([', '.join(b) for b in chunks])
    return line


def play_all_this(timer, THEME, SECOND_PER_BAR):
    play_lines = []
    for idx in range(len(THEME)):
        joined = join_with_newline(THEME[:idx+1])
        play_lines.append([timer, joined])
        timer += SECOND_PER_BAR
    return play_lines, timer


def sample(theme, indices):
    return [theme[i-1] for i in indices]


def main():
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('processdir')
    args = parser.parse_args()

    IDIR = args.processdir
    arrange_ifile = '{}/{}'.format(IDIR, ARRANGE_FILENAME)
    assert os.path.exists(arrange_ifile), 'Arrangement file not found'

    arrangement = json.load(open(arrange_ifile))

    caption_json = {}
    caption_json['start'] = arrangement['start']
    caption_json['duration'] = 60
    caption_json['audioDelay'] = 0

    composition_name = arrangement['composition']
    assert composition_name in THEMES, 'Unknown composition'

    composition = THEMES[composition_name]
    THEME = composition['theme'].split()
    KHALI = composition['khali'].split()

    # Expand all variations for this theme
    variations = {}
    for variation_name, variation in VARIATIONS.iteritems():
        expanded_variation = []
        for row in variation:
            sample_from = row[0]
            if sample_from == 'raw':
                expanded_variation += row[1:]
            else:
                if sample_from == 'theme':
                    source = THEME
                elif sample_from == 'khali':
                    source = KHALI
                expanded_variation += sample(source, row[1:])
        variations[variation_name] = expanded_variation

    text = []
    BPM = arrangement['bpm']
    SECOND_PER_BAR = 60.0 / BPM
    timer = 0
    for piece in arrangement['arrangement']:
        if piece['time'] != -1:
            timer = piece['time']

        if piece['part'] == 'variation':
            notes = variations[piece['idx']]
            part1 = notes[:len(notes)/2]
            part2 = notes[len(notes)/2:]

            lines, timer = play_all_this(timer, part1, SECOND_PER_BAR)
            text += lines

            lines, timer = play_all_this(timer, part2, SECOND_PER_BAR)
            text += lines
        else:
            if piece['part'] == 'theme':
                notes = THEME
            elif piece['part'] == 'khali':
                notes = KHALI

            lines, timer = play_all_this(timer, notes, SECOND_PER_BAR)
            text += lines
    caption_json['text'] = text

    ofilename = '{}/{}'.format(IDIR, CAPTION_FILENAME)
    ofile = open(ofilename, 'w')
    json.dump(caption_json, ofile, indent=4)
    ofile.close()


main()
