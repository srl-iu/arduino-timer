#!/usr/bin/env python
"""
#
# By: Charles Brandt [code at charlesbrandt dot com]
# On: *2015.02.09 15:17:30 
# License: MIT 
# Requires:
#
# Description:
#
"""

import os, sys, codecs, re

def usage():
    print __doc__
    
def check_min_max(diff, maximum, minimum, position):
    #print "CHECKING!"
    #print "ABSOLUTE: ", abs(diff)
    if abs(diff) > maximum:
        maximum = abs(diff)
        print "NEW MAX FOUND: %s at %s" % (maximum, position)
    if abs(diff) < minimum:
        minimum = abs(diff)
        #print "NEW MIN FOUND: %s at %s" % (minimum, position)

    #print "MIN / MAX:", minimum, maximum
    return maximum, minimum

def compare_times(source, destination):
    f = codecs.open(source, 'r', encoding='utf-8')

    trials = []
    for line in f.readlines()[1:]:
        (num, actual, t1, t2, t3, wave, stamp) = line.split(',')
        trials.append( [ num, actual, t1, t2, t3, wave, stamp ] )

    f.close()

    diff_max = 0
    diff_min = 100000000

    diff_max_raw = 0
    diff_min_raw = 100000000

    ratio_total = 0
    ratio_count = 0

    diff_total = 0
    
    for trial in trials:
        [ num, actual, t1, t2, t3, wave, stamp ] = trial

        #special check
        #if not num in [ '536' ]:
        #if not num in [ '545' ]:
        if not num in [  ]:
            actual_us = float(actual) * 1000.0

            count = 0
            total = 0
            for t in [ t1, t2, t3 ]:
                t = float(t)
                if t > 0:
                    raw_diff = actual_us - t
                    (diff_max_raw, diff_min_raw) = check_min_max(raw_diff, diff_max_raw, diff_min_raw, ratio_count)
                    total += t
                    count += 1

            average = total * 1.0 / count
            diff = (actual_us) - average
            (diff_max, diff_min) = check_min_max(diff, diff_max, diff_min, ratio_count)

            if abs(diff) > 1000:
                print trial

            diff_total += abs(diff)

            ratio = diff * 1.0 / actual_us 
            #print diff, actual_us, ratio
            ratio_total += ratio
            ratio_count += 1

    ratio_average = ratio_total / ratio_count
    diff_average = diff_total * 1.0 / ratio_count

    print
    print "Max differences: %s (average) %s (raw)" % (diff_max, diff_max_raw)
    print "Min differences: %s (average) %s (raw)" % (diff_min, diff_min_raw)
    print "Average diff: %s" % diff_average
    print
    print "frequency mismatch (clock_adjust):"
    print ratio_average
    


def main():
    #requires that at least one argument is passed in to the script itself
    #(through sys.argv)
    if len(sys.argv) > 1:
        helps = ['--help', 'help', '-h']
        for i in helps:
            if i in sys.argv:
                usage()
                exit()
        source = sys.argv[1]
        if len(sys.argv) > 2:
            destination = sys.argv[2]
        else:
            destination = None

        compare_times(source, destination)

    else:
        # look for a single run and use that instead
        destination = None
        matches = []
        items = os.listdir("output")
        for item in items:
            if re.match('timer_test-', item):
                matches.append(item)
        if len(matches) == 1:
            #print matches
            source = os.path.join('output', matches[0])
            compare_times(source, destination)
        elif len(matches) > 1:
            print "More than one timer-test result found. please specify which one you want to use:"
            print matches
        else:
            usage()
            exit()
        
if __name__ == '__main__':
    main()
