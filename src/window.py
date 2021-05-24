# window.py
#
# Copyright 2021 Will Taylor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
gi.require_version('Handy', '1')
from gi.repository import Handy
Handy.init()

import json
from . import config

class PurismCVWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'PurismCVWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        path = f"{config.pkgdatadir}/profile.json"
        try:
            with open(path, "r") as json_file:
                self.profile_data = json.load(json_file)
        except:
            self.profile_data = \
            {
                "name"       : "First Last",
                "email"      : "name@email.com",
                "phone"      : "(123) 456-7890",
                "about"      : "I am a person who does stuff.",
                "skills"     : [["python.svg", "Python"]],
                "experience" : ["A\n", "B\n\n"],
                "education"  : ["BA, School of Stuff\n",
                                "PhD, University of Things"]
             }

        title_bar = Handy.TitleBar()
        name = self.profile_data["name"]
        header = Gtk.HeaderBar(title=f"{name}'s CV", show_close_button=True)
        title_bar.add(header)
        self.set_titlebar(title_bar)

        self.leaflet = Handy.Leaflet(transition_type = "slide")

        # Need default pages to help the Leaflet know whether it starts
        # folded or not, combined with a default size
        # Start folded
        self.set_default_size(360, 648)

        # Default Page 1 is a sidebar with profile info and buttons to expand
        # extra info. App starts mobile-friendly by default
        page_1 = self.write_page_1(True)

        # Default Page 2 is the summary page. This is a farily arbitrary choice.
        # Just one some second page to have ready by default.
        contents = "".join(text for text in self.profile_data["summary"])
        page_2 = self.write_page_2(contents, True)

        self.leaflet.add(page_1)
        self.leaflet.child_set(page_1, name="Page 1")
        self.leaflet.add(page_2)
        self.leaflet.child_set(page_2, name="Page 2")
        self.leaflet.connect("notify::folded", self.on_fold_change)

        self.add(self.leaflet)
        self.show_all()

    def write_page_1(self, folded):
        """
        This function sets up page 1, which is always a sidebar of profile data
        and buttons to show the full contents of the other profile sections.

        When unfolded, the buttons get hidden by the on_fold_change function.
        """

        page = Gtk.Box(orientation = "horizontal", halign = "start",
                       hexpand = False)
        profile_box = Gtk.Box(orientation = "vertical")

        path        = f"{config.pkgdatadir}/images/profile_pic.png"
        profile_pic = Gtk.Image.new_from_file(path)

        profile_list = Gtk.ListBox()
        name_row     = Handy.ActionRow(title     = "Name",
                                       subtitle  = self.profile_data["name"],
                                       icon_name = "my-person-symbolic")
        email_row    = Handy.ActionRow(title     = "Email",
                                       subtitle  = self.profile_data["email"],
                                       icon_name = "my-mail-message-new-symbolic")
        phone_row    = Handy.ActionRow(title     = "Phone",
                                       subtitle  = self.profile_data["phone"],
                                       icon_name = "my-phone-symbolic")
        about_row    = Handy.ActionRow(title     = "About",
                                       icon_name = "my-about-symbolic")

        about        = "".join(text for text in self.profile_data["about"])
        buffer       = Gtk.TextBuffer(text = about)
        textview     = Gtk.TextView(buffer      = buffer,
                                    wrap_mode   = "word",
                                    top_margin  = 10,
                                    left_margin = 10)
        about_window = Gtk.ScrolledWindow(propagate_natural_width = False,
                                             valign = "fill",
                                             vexpand = True)
        about_window.add_with_viewport(textview)


        profile_list.add(name_row)
        profile_list.add(email_row)
        profile_list.add(phone_row)
        profile_list.add(about_row)

        skills       = self.profile_data["skills"]
        skills_row   = Handy.ActionRow(title     = "Skills",
                                       icon_name = "my-skills-symbolic")
        skills_list  = Gtk.ListBox()
        for skill in skills:
            # Skills should be listed as [icon, skill]
            row = Handy.ActionRow(subtitle = skill[1],
                                  icon_name = skill[0])
            skills_list.add(row)

        skill_window = Gtk.ScrolledWindow(propagate_natural_width = False,
                                             valign = "fill",
                                             vexpand = True)
        skill_window.add_with_viewport(skills_list)

        profile_box.add(profile_pic)
        profile_box.add(profile_list)
        profile_box.add(about_window)
        profile_box.add(skills_row)
        # profile_box.add(skills_list)
        profile_box.add(skill_window)
        page.add(profile_box)

        button_box = Gtk.Box(orientation = "vertical", halign="start")

        summary_button    = Gtk.Button(label = "Summary"   , halign = "fill")
        summary_button.connect('clicked', self.show_page_2, "summary")
        experience_button = Gtk.Button(label = "Experience", halign = "fill")
        experience_button.connect('clicked', self.show_page_2, "experience")
        education_button  = Gtk.Button(label = "Education" , halign = "fill")
        education_button.connect('clicked', self.show_page_2, "education")

        button_box.add(summary_button)
        button_box.add(experience_button)
        button_box.add(education_button)

        page.add(button_box)

        page.button_box = button_box

        return page

    def write_page_2(self, page_contents_markup, add_button):
        """
        This function writes a new page 2 with the provided contents.
        It just writes the contents and, optionally, provides a back button.

        The back button is used when writing a folded page. Otherwise, there
        is no back button.
        """

        page         = Gtk.Box(orientation = "vertical", hexpand = True,
                               margin = 20)

        label   = Gtk.Label(wrap = True, valign="start")
        label.set_markup(page_contents_markup)

        scrolled_window = Gtk.ScrolledWindow(propagate_natural_width = False,
                                             vexpand = True)
        scrolled_window.add_with_viewport(label)

        page.add(scrolled_window)
        if (add_button):
            back_button  = Gtk.Button(label = "Go Back", halign = "center")
            page.add(back_button)
            back_button.connect('clicked', self.show_page_1)

        return page

    def show_page_1(self, button):
        self.leaflet.set_visible_child_name("Page 1")

    def show_page_2(self, button, page_name):
        """
        This function handles which page is to become page 2.
        It deletes the existing page two, then rewrites page 2 to have the
        appropriate contents, based on which button was clicked.
        """

        contents = "".join(text for text in self.profile_data[page_name])
        page     = self.write_page_2(contents, True)

        if (len(self.leaflet.get_children()) > 1):
            self.leaflet.remove(self.leaflet.get_child_by_name("Page 2"))

        self.leaflet.add(page)
        self.leaflet.child_set(page, name="Page 2")
        self.leaflet.set_visible_child_name("Page 2")

        self.show_all()

    def on_fold_change(self, leaflet, folded):
        """
        This function handles switching between folded and unfolded.
        Whenever the leaflet gets folded, display page 1.

        Whenever the leaflet is unfolded, write a new page 2 that contains
        every section, rather than just one.

        Both pages are displayed when unfolded.
        """

        page_1 = self.leaflet.get_child_by_name("Page 1")
        if (leaflet.get_folded()):
            print("Folded")
            box_visible = True
            self.leaflet.set_visible_child_name("Page 1")
        else:
            print("Unfolded")
            box_visible = False
            page = Gtk.Box(orientation = "horizontal")

            contents   = "".join(text for text in self.profile_data["summary"])
            summary    = self.write_page_2(contents, False)
            contents   = "".join(text for text in self.profile_data["experience"])
            experience = self.write_page_2(contents, False)
            contents   = "".join(text for text in self.profile_data["education"])
            education  = self.write_page_2(contents, False)

            page.add(summary)
            page.add(experience)
            page.add(education)

            if (len(self.leaflet.get_children()) > 1):
                self.leaflet.remove(self.leaflet.get_child_by_name("Page 2"))

            self.leaflet.add(page)
            # These lines aren't strictly necessary, but they seem to help
            # smooth out the animations when unfolding.
            self.leaflet.child_set(page, name="Page 2")
            self.leaflet.set_visible_child_name("Page 2")

        self.leaflet.show_all()

        # Hide the page 1's buttons that show the individual section page 2s
        # when unfolded.
        page_1.button_box.set_visible(box_visible)
