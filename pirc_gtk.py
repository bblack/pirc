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
        self.logbox.set_cursor_visible(False)
        self.logbox.set_wrap_mode(gtk.WRAP_WORD)
        self.logbox.show()
        self.logscrollbox = gtk.ScrolledWindow()
        self.logscrollbox.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.logscrollbox.add(self.logbox)
        self.logscrollbox.show()

        self.nickbox = gtk.TreeView(gtk.ListStore(gobject.TYPE_STRING))
        self.nickbox.set_headers_visible(False)
        nick_col = gtk.TreeViewColumn('Nick')
        # TODO: figure out what the shit is going on here
        cell_renderer = gtk.CellRendererText()
        nick_col.pack_start(cell_renderer)
        nick_col.set_attributes(cell_renderer, text=0)
        self.nickbox.append_column(nick_col)
        self.nickbox.show_all()

        self.entry = gtk.Entry()
        self.entry.show()

    def _writeline(self, str):
        vadj = self.logscrollbox.get_vadjustment()
        print 'vadj upper/lower/page_size/value is {0}/{1}/{2}/{3}'.format(vadj.upper,vadj.lower,vadj.page_size,vadj.value)
        scrollbar_was_at_bottom = (vadj.value + vadj.page_size >= vadj.upper)
        print scrollbar_was_at_bottom

        str = str.rstrip('\r\n')
        buf = self.logbox.get_buffer()
        iter = buf.get_end_iter()
        buf.insert(iter, str + '\r\n')

        if scrollbar_was_at_bottom:
             vadj.set_value(vadj.upper)

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
        self.channel.nick_added += self.handle_nick_added
        self.channel.nick_removed += self.handle_nick_removed
        self.channel.nick_changed += self.handle_nick_changed
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
        gtk.gdk.threads_enter()
        try:
            self._writeline('<{0}> {1}'.format(user.nick, msg_text))
        finally:
            gtk.gdk.threads_leave()

    def handle_nick_added(self, channel, nick):
        gtk.gdk.threads_enter()
        try:
            self._add_nick_to_nickbox(nick)
        finally:
            gtk.gdk.threads_leave()

    def handle_nick_removed(self, channel, nick):
        gtk.gdk.threads_enter()
        try:
            self._remove_nick_from_nickbox(nick)
        finally:
            gtk.gdk.threads_leave()

    def handle_nick_changed(self, channel, old_nick, new_nick):
        gtk.gdk.threads_enter()
        try:
            self._change_nick_in_nickbox(old_nick, new_nick)
            self._writeline('{0} is now known as {1}'.format(old_nick, new_nick))
        finally:
            gtk.gdk.threads_leave()

    def _add_nick_to_nickbox(self, nick):
        print 'adding nick to box'
        self.nickbox.get_model().append([nick])
        print 'added nick to box'

    def _remove_nick_from_nickbox(self, nick):
        matching_iters = []
        self.nickbox.get_model().foreach(self.iter_matches_nick, (matching_iters, nick))
        self.nickbox.get_model().remove(matching_iters[0])

    def _change_nick_in_nickbox(self, old_nick, new_nick):
        matching_iters = []
        self.nickbox.get_model().foreach(self.iter_matches_nick, (matching_iters, old_nick))
        self.nickbox.get_model().set(matching_iters[0], 0, new_nick)

    def iter_matches_nick(self, model, path, iter, (matching_iters, nick_sought)):
        nick = self.nickbox.get_model().get_value(iter, 0)
        if nick == nick_sought:
            print 'found matching nick'
            matching_iters.append(iter)
        return False




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
        #print 'handling channel opened by idle_adding make_channel_tab'
        #gobject.idle_add(self.make_channel_tab, new_channel)

        gtk.gdk.threads_enter()
        try:
            self.make_channel_tab(new_channel)
        finally:
            gtk.gdk.threads_leave()


    def make_channel_tab(self, channel):
        channel_widget = ChannelWidget(channel)
        channel_widget.show()
        self.notebook.append_page(channel_widget, gtk.Label(channel.name))
        #TODO: insert it immediately after the right server tab
        self.notebook.set_current_page(self.notebook.page_num(channel_widget))

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
    conn.connect('irc.whatnet.org', 6667, 'pi')

    try:
        pirc_gtk.main()
    except KeyboardInterrupt:
        pirc_gtk.world.shut_it_down()
        raise



