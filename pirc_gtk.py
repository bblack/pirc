#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk
import gobject
from libpirc.connection import Connection
from libpirc.world import World
from test import Test

class ChatWidget(gtk.VBox):

    def __init__(self):
        super(ChatWidget, self).__init__(False)

        self.logbox = gtk.TextView()
        self.logbox.set_editable(False)
        self.logbox.show()
        self.logscrollbox = gtk.ScrolledWindow()
        self.logscrollbox.add_with_viewport(self.logbox)
        self.logscrollbox.show()

        self.nickbox = gtk.TreeView()
        self.nickbox.show()

        self.entry = gtk.Entry()
        self.entry.show()

    def _writeline(self, str):
        str = str.rstrip('\r\n')
        buf = self.logbox.get_buffer()
        iter = buf.get_end_iter()
        buf.insert(iter, str + '\r\n')

class ServerWidget(ChatWidget):
    def __init__(self, connection):
        super(ServerWidget, self).__init__()
        self.entry.connect("activate", self.handle_text_entered)
        self.connection = connection

        # and also subscribe to connection's events here!
        self.connection.received += self.handle_received
        self.connection.sent += self.handle_sent

        self.pack_start(self.logscrollbox)
        self.pack_start(self.entry, False)

    def handle_text_entered(self, widget, data=None):
        words = self.entry.get_text().split(' ')
        if words[0] == '/server':
            self.connection.connect(words[1], 6667, 'pi') #hack
        else:
            self.connection.writeline(self.entry.get_text())
        self.entry.set_text('')

    def handle_received(self, msg):
        gobject.idle_add(self._writeline, ('  >> ' + msg))

    def handle_sent(self, msg):
        gobject.idle_add(self._writeline, ('<<   ' + msg))

class ChannelWidget(ChatWidget):
    def __init__(self, channel):
        super(ChannelWidget, self).__init__()
        self.channel = channel
        # and also subscribe to channel's events here!
        self.channel.msg_received += self.handle_msg_received
        # #self.channel.nick_added += handle_nick_added
        # #self.channel.nick_removed += handle_nick_removed
        # self.channel.nick_changed += self.handle_nick_changed
        # self.channel.someone_kicked += self.handle_someone_kicked
        # self.channel.someone_joined += self.handle_someone_joined
        # self.channel.someone_parted += self.handle_someone_parted
        # self.channel.someone_quit += self.handle_someone_quit

        self.log_and_nicks_box = gtk.HPaned()
        self.log_and_nicks_box.add1(self.logscrollbox)
        self.log_and_nicks_box.add2(self.nickbox)
        self.log_and_nicks_box.set_position(300) # hack
        self.log_and_nicks_box.show()

        self.pack_start(self.log_and_nicks_box)
        self.pack_start(self.entry, False)

    def handle_msg_received(self, channel, user, msg_text):
        gobject.idle_add(self._writeline, '<{0}> {1}'.format(user.nick, msg_text))



class PircGtk:

    def delete_event(self, widget, event, data=None):
        print "delete event occurred"
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        self.world.shut_it_down()
        gtk.main_quit()

    def handle_connection_added(self, world, new_connection):
        gobject.idle_add(self.make_server_tab, new_connection)

    def handle_channel_opened(self, world, new_channel):
        gobject.idle_add(self.make_channel_tab, new_channel)

    def make_channel_tab(self, channel):
        channel_widget = ChannelWidget(channel)
        channel_widget.show()
        self.notebook.append_page(channel_widget, gtk.Label(channel.name)) #TODO: insert it immediately after the right server tab

    def make_server_tab(self, connection):
        chat_widget = ServerWidget(connection)
        chat_widget.show()
        self.notebook.append_page(chat_widget, gtk.Label('a server'))

    def __init__(self, world):
        self.world = world
        self.world.connection_added += self.handle_connection_added
        self.world.channel_opened += self.handle_channel_opened

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)
        self.window.set_default_size(640, 480)

        self.notebook = gtk.Notebook()
        self.notebook.show()
        self.window.add(self.notebook)
        
        self.window.show()

    def main(self):
        gtk.gdk.threads_init()
        gtk.main()


if __name__ == "__main__":
    world = World()
    pirc_gtk = PircGtk(world)

    conn = world.new_connection()

    try:
        pirc_gtk.main()
    except KeyboardInterrupt:
        pirc_gtk.world.shut_it_down()
        raise



