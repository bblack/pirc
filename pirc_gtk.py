#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk

class ChatWidget(gtk.VBox):

    def __init__(self):
        super(ChatWidget, self).__init__(False)

        self.log_and_nicks_box = gtk.HPaned()
        self.logbox = gtk.TextView()
        self.logbox.set_editable(False)
        self.logbox.show()
        self.nickbox = gtk.TreeView()
        self.nickbox.show()
        self.log_and_nicks_box.add1(self.logbox)
        self.log_and_nicks_box.add2(self.nickbox)
        self.log_and_nicks_box.show()

        self.entry = gtk.Entry()
        self.entry.show()

        self.pack_start(self.log_and_nicks_box)
        self.pack_start(self.entry, False)

class ServerWidget(ChatWidget):
    def __init__(self, connection):
        super(ServerWidget, self).__init__()
        self.connection = connection
        # and also subscribe to connection's events here!

class ChannelWidget(ChatWidget):
    def __init__(self, channel):
        super(ChannelWidget, self).__init__()
        self.channel = channel
        # and also subscribe to channel's events here!

class PircGtk:

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
        self.window.set_default_size(640, 480)

        self.chat_widget = ChatWidget()
        self.chat_widget.show()
        self.window.add(self.chat_widget)
        self.window.show()

    def main(self):
        gtk.main()


if __name__ == "__main__":
    pirc_gtk = PircGtk()
    pirc_gtk.main()
