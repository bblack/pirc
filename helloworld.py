#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk

class HelloWorld:

    def delete_event(self, widget, event, data=None):
        print "delete event occurred"
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)

        self.log_and_nicks_box = gtk.HPaned()
        self.logbox = gtk.TextView()
        self.logbox.show()
        self.nickbox = gtk.TreeView()
        self.nickbox.show()
        self.log_and_nicks_box.add1(self.logbox)
        self.log_and_nicks_box.add2(self.nickbox)
        self.log_and_nicks_box.show()

        self.entry = gtk.Entry()
        self.entry.show()

        self.vbox = gtk.VBox(False)
        self.vbox.pack_start(self.log_and_nicks_box)
        self.vbox.pack_start(self.entry, False)
        self.vbox.show()
        self.window.add(self.vbox)

        self.window.show()

    def main(self):
        gtk.main()
if __name__ == "__main__":
    hello = HelloWorld()
    hello.main()
