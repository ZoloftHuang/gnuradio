"""
Copyright 2013 Free Software Foundation, Inc.
This file is part of GNU Radio

GNU Radio Companion is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

GNU Radio Companion is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

from __future__ import absolute_import

import six

from gi.repository import Gtk, GObject

from .Constants import MIN_DIALOG_WIDTH, MIN_DIALOG_HEIGHT


class ParserErrorsDialog(Gtk.Dialog):
    """
    A dialog for viewing parser errors
    """

    def __init__(self, error_logs):
        """
        Properties dialog constructor.

        Args:
            block: a block instance
        """
        GObject.GObject.__init__(self, title='Parser Errors', buttons=(Gtk.STOCK_CLOSE, Gtk.ResponseType.ACCEPT))

        self._error_logs = None
        self.tree_store = Gtk.TreeStore(str)
        self.update_tree_store(error_logs)

        column = Gtk.TreeViewColumn('XML Parser Errors by Filename')
        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 0)
        column.set_sort_column_id(0)

        self.tree_view = tree_view = Gtk.TreeView(self.tree_store)
        tree_view.set_enable_search(False)  # disable pop up search box
        tree_view.set_search_column(-1)  # really disable search
        tree_view.set_reorderable(False)
        tree_view.set_headers_visible(False)
        tree_view.get_selection().set_mode(Gtk.SelectionMode.NONE)
        tree_view.append_column(column)

        for row in self.tree_store:
            tree_view.expand_row(row.path, False)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(tree_view)

        self.vbox.pack_start(scrolled_window, True)
        self.set_size_request(2*MIN_DIALOG_WIDTH, MIN_DIALOG_HEIGHT)
        self.show_all()

    def update_tree_store(self, error_logs):
        """set up data model"""
        self.tree_store.clear()
        self._error_logs = error_logs
        for filename, errors in six.iteritems(error_logs):
            parent = self.tree_store.append(None, [str(filename)])
            try:
                with open(filename, 'r') as fp:
                    code = fp.readlines()
            except EnvironmentError:
                code = None
            for error in errors:
                # http://lxml.de/api/lxml.etree._LogEntry-class.html
                em = self.tree_store.append(parent, ["Line {e.line}: {e.message}".format(e=error)])
                if code:
                    self.tree_store.append(em, ["\n".join(
                        "{} {}{}".format(line, code[line - 1].replace("\t", "    ").strip("\n"),
                                         " " * 20 + "<!-- ERROR -->" if line == error.line else "")
                        for line in range(error.line - 2, error.line + 3) if 0 < line <= len(code)
                    )])

    def run(self):
        """
        Run the dialog and get its response.

        Returns:
            true if the response was accept
        """
        response = Gtk.Dialog.run(self)
        self.destroy()
        return response == Gtk.ResponseType.ACCEPT
