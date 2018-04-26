#! /usr/bin/env python

def join_with_newline(bars):
    chunks = []
    PERLINE = 4
    for idx in range(0, len(bars), PERLINE):
        chunks.append(bars[idx:idx+PERLINE])
    line = '\\n'.join([', '.join(bars) for bars in chunks])
    return line



def play_all_this(timer, THEME):
    for idx in range(len(THEME)):
        joined = join_with_newline(THEME[:idx+1])
        print '\t[{}, "{}"],'.format(timer, joined)
        timer += SECOND_PER_BAR
    return timer


def sample(theme, indices):
    return [theme[i] for i in indices]
    
# HARDCODING FOR NOW
BPM = 140
START_AT = 57
THEME = "Dha-TR KTGeRe DeReDeRe KTTK Dha-TR KTTK Tu-Na- KTTK".split()
KHALI = "Ta-TR KTKeRe TeReTeRe KTTK Ta-TR KTTK Dhin-Na- GeReNaGe".split()
VARIATION_1 = sample(THEME, range(4) + range(4) + range(8))
VARIATION_1 += sample(KHALI, range(4) + range(4)) + sample(THEME, range(8))
VARIATION_2 = sample(THEME, range(3) + range(3) + range(2) + range(8))
VARIATION_2 += sample(KHALI, range(3) + range(3) + range(2)) + sample(THEME, range(8))

# First group
SECOND_PER_BAR = 60.0/1 * 1/140.0
timer = 3 + START_AT
timer = play_all_this(timer, THEME)
timer = play_all_this(timer, KHALI)
timer = play_all_this(timer, THEME)
timer = play_all_this(timer, KHALI)


timer = 22.5 + 0.8 + START_AT
timer = play_all_this(timer, VARIATION_1)


timer = 40.4 + START_AT
timer = play_all_this(timer, VARIATION_2)
