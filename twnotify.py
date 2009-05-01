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

import gtk, urllib, os, pynotify, re, sys, time
from ConfigParser import ConfigParser
from xml.etree import ElementTree

class TwNotify:
    def __init__(self, icons=True):
        self.seen = {}
        self.icons = icons
        self.conffile = os.environ['HOME']+'/.config/twnotify/config'
        if icons:
            self.icondir = os.environ['HOME']+'/.cache/twnotify'
            if not os.path.isdir(self.icondir):
                os.makedirs(self.icondir)
        pynotify.init('TwNotify')
        self.checkfeed(notify=False)

    def run(self, timeout=300):
        while True:
            time.sleep(timeout)
            self.checkfeed()

    def checkfeed(self, notify=True):
        conf = ConfigParser()
        conf.readfp(open(self.conffile))
        file = urllib.urlopen('https://%s:%s@twitter.com/statuses/friends_timeline.xml' % (conf.get('Authentication','username'), conf.get('Authentication','password')))
        del conf # try not to leave passwords in memory for too long
        statuses = ElementTree.fromstring(file.read())
        file.close()
        del file
        for status in reversed(statuses):
            status_id = status.find('id').text
            if notify and status_id not in self.seen:
                author = status.find('user/screen_name').text
                msg = status.find('text').text
                icon = None
                if self.icons:
                    iconurl = status.find('user/profile_image_url').text
                    uid = status.find('user/id').text
                    file = re.match('.*/(.+)$', iconurl).group(1)
                    iconuid = self.icondir+'/'+uid
                    iconfile = self.icondir+'/'+uid+'/'+file
                    if not os.path.isfile(iconfile):
                        if not os.path.isdir(iconuid):
                            os.makedirs(iconuid)
                        with open(iconfile,'w+') as fo:
                            fo.write(urllib.urlopen(iconurl).read())
                    icon = iconfile

                self.notify(author, msg, icon=icon)
            self.seen[status_id] = True
        del statuses

    def notify(self, title, body, icon=None):
        n = pynotify.Notification(title, body)
        if icon:
            i = gtk.gdk.pixbuf_new_from_file(icon)
            n.set_icon_from_pixbuf(i)
        n.show()

if __name__ == '__main__':
    tw = TwNotify()
    if len(sys.argv) > 1:
        tw.run(int(sys.argv[1]))
    else:
        tw.run()
