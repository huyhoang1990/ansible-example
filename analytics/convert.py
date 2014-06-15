#! coding: utf-8

from __future__ import division
import sys
import os
import re



def convert_image(folder):
    images = os.listdir(folder)

    display_times = []
    for image in images:
        groups = re.findall('\d+', image)
        if groups:
            display_times.append(int(groups[0]))

    display_times = sorted(display_times)
    # display_times = sorted([int(re.findall('\d+', image)[0])
    #                  for image in images])

    print display_times
    duration_times = []

    # duration_times.append(display_times[0])
    last_index = len(display_times) - 1

    for index, value in enumerate(display_times):
        if (index != last_index):
            duration_times.append(display_times[index + 1] -
                                  display_times[index])

    print display_times
    print duration_times

    display_times.pop(0)
    # f = open('concat.txt', 'a')
    f = open('concat', 'w')
    f.write('ffconcat version 1.0\n')
    f.write('file screenshot0.png\n')
    f.write('duration 0\n')
    f.write('file screenshot0.png\n')
    for index, duration_time in enumerate(duration_times):
        f.write('duration %s \n' % float(duration_time / 1000))
        f.write('file screenshot-%s.png \n' % display_times[index])

    f.close()

if __name__ == '__main__':
    folder = sys.argv[1]
    convert_image(folder)

