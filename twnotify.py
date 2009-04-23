#!/usr/bin/env python
# encoding: UTF-8

# Copyright © 2009, Tom Adams
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
# OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Kludge for 2.x
import sys; reload(sys); sys.setdefaultencoding('utf-8')

import feedparser, urllib, os, re, subprocess, sys, time, yaml

class TwNotify:
    def __init__(self):
        self.seen = {}
        self.checkfeed(notify=False)

    def run(self, timeout=300):
        while True:
            time.sleep(timeout)
            self.checkfeed()

    def checkfeed(self, notify=True):
        auth = yaml.load(open(os.environ['HOME']+'/.twitterauth'))
        file = urllib.urlopen('https://%s:%s@twitter.com/statuses/friends_timeline.atom' % (auth['Username'], auth['Password']))
        del auth # try not to leave passwords in memory for too long
        feed = feedparser.parse(file)
        file.close()
        for entry in reversed(feed.entries):
            if notify and not self.seen.has_key(entry.id):
                author, msg = re.match('^(.*?): (.*)$', entry.title).group(1,2)
                self.notify(author, msg)
            self.seen[entry.id] = True

    def notify(self, title, body):
        if subprocess.call(['notify-send', title, body]) != 0:
            raise Exception("didn't work")

if __name__ == '__main__':
    tw = TwNotify()
    if len(sys.argv) > 1:
        tw.run(int(sys.argv[1]))
    else:
        tw.run()
