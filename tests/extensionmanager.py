# -*- coding: utf-8 -*-

# Copyright (C) 2017 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.


import unittest


from appkit import extensionmanager


class PluginTypeA(extensionmanager.Extension):
    pass


class PluginTypeB(extensionmanager.Extension):
    pass


class FooExtension1(PluginTypeA):
    __extension_name__ = 'foo1'
    pass


class FooExtension2(PluginTypeA):
    __extension_name__ = 'foo2'
    pass


class BarExtension1(PluginTypeB):
    __extension_name__ = 'bar1'
    pass


class BarExtension2(PluginTypeB):
    __extension_name__ = 'bar2'
    pass


class ExtensionManagerTest(unittest.TestCase):
    def get_em(self,
               *args,
               name='testapp', extension_points=None, extension_classes=None,
               **kwargs):
        em = extensionmanager.ExtensionManager(*args, name=name, **kwargs)
        if extension_points:
            for ep in extension_points:
                em.register_extension_point(ep)

        if extension_classes:
            for ec in extension_classes:
                em.register_extension_class(ec)

        return em

    def test_simple_register(self):
        em = self.get_em(
            extension_points=[PluginTypeA, PluginTypeB],
            extension_classes=[FooExtension1, BarExtension1])

        extension = em.get_extension(PluginTypeA, 'foo1')
        self.assertTrue(
            isinstance(extension, PluginTypeA)
        )

    def test_extensions_query(self):
        em = self.get_em(
            extension_points=[PluginTypeA, PluginTypeB],
            extension_classes=[FooExtension1, FooExtension2,
                               BarExtension1, BarExtension2])

        type_a_exts = dict(em.get_extensions_for(PluginTypeA))
        extension_names = list(type_a_exts.keys())
        extension_objects = list(type_a_exts.values())
        self.assertEqual(
            set(['foo1', 'foo2']),
            set(extension_names))

        self.assertTrue(
            all([isinstance(x, PluginTypeA) for x in extension_objects]))


if __name__ == '__main__':
    unittest.main()
