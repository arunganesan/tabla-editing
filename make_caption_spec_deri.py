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
    return [theme[i-1] for i in indices]
    
# HARDCODING FOR NOW
BPM = 140
THEME = "Dha GTK TNTi NGN DhaNaG GTK TNTi NKN".split()
KHALI = "Ta KTK TNTi NKN DhaNaG GTK DheNeDhi NGN".split()

VARIATION_1 = sample(THEME, [1,2,3,1,2,3,1,2] + range(1,9))
VARIATION_1 += sample(KHALI, [1,2,3,1,2,3,1,2]) + sample(THEME, range(1,9))

VARIATION_2 = sample(THEME, [2,2,3,4,2,2,3,4] + range(1,9))
VARIATION_2 += sample(KHALI, [2,2,3,4,2,2,3,4]) + sample(THEME, range(1,9))

VARIATION_3 = sample(THEME, [2,2,2,2,3,4,3,4] + range(1,9))
VARIATION_3 += sample(KHALI, [2,2,2,2,3,4,3,4]) + sample(THEME, range(1,9))


# First group
SECOND_PER_BAR = 60.0/1 * 1/140.0
timer = 76 + 0.75
timer = play_all_this(timer, THEME)
timer = play_all_this(timer, KHALI)
timer = play_all_this(timer, THEME)
timer = play_all_this(timer, KHALI)

timer = play_all_this(timer, VARIATION_1)

timer = 60+51
timer = play_all_this(timer, VARIATION_2)
timer = play_all_this(timer, VARIATION_3)

print "]}"
