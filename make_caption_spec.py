#! /usr/bin/env python

def join_with_newline(bars):
    chunks = []
    PERLINE = 4
    for idx in range(0, len(bars), PERLINE):
        chunks.append(bars[idx:idx+PERLINE])
    line = '\n'.join([', '.join(bars) for bars in chunks])
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


IFILE = 'arrangement.json'
OFILE = 'caption.json'

def main():
    import argparse
    import json, os
    
    #parser = argparse.ArgumentParser()
    #parser.add_argument('processdir')
    #args = parser.parse_args()
    
    

    caption_json = {}
    arrangement = json.load(open(IFILE))
    
    caption_json['start'] = arrangement['start']
    caption_json['duration'] = 60
    caption_json['audioDelay'] = 0

    library_ifile = arrangement['library']
    assert os.path.exists(library_ifile)
    library = json.load(open(library_ifile))
    THEME = library['theme'].split()
    KHALI = library['khali'].split()
    
    variations = []
    for variation in library['variations']:
        expanded_variation = []
        for row in variation:
            if row[0] == 'theme':
                source = THEME
            else:
                source = KHALI
            
            expanded_variation += sample(source, row[1:])
        variations.append(expanded_variation)
    
    text = []
    BPM = arrangement['bpm']
    SECOND_PER_BAR = 60.0 / BPM
    timer = 0
    for piece in arrangement['arrangement']:
        if piece['time'] != -1:
            timer = piece['time']
        
        if piece['part'] == 'theme':
            notes = THEME
        elif piece['part'] == 'khali':
            notes = KHALI
        elif piece['part'] == 'variation':
            notes = variations[piece['idx']-1]

        lines, timer = play_all_this(timer, notes, SECOND_PER_BAR)
        text += lines
    caption_json['text'] = text

    ofile = open(OFILE, 'w')
    json.dump(caption_json, ofile, indent=4)
    ofile.close()
main()
