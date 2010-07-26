# (C) Copyright 2010 Georges Racinet <georges@racinet.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

from Products.CPSSchemas.Field import FieldRegistry
from Products.CPSSchemas.BasicFields import CPSStringField
from Products.CPSSchemas.BasicFields import CPSAsciiStringField

class CPSStringOrNoneField(CPSStringField):
    """String fields accepting None as a value."""

    meta_type = "CPS String or None Field"

    def validate(self, v):
        if v is None:
            return v
        return CPSStringField.validate(self, v)

FieldRegistry.register(CPSStringOrNoneField)


class CPSAsciiStringOrNoneField(CPSStringField):
    """Ascii string field accepting also None as a value."""

    meta_type = "CPS Ascii String or None Field"

    def validate(self, v):
        if v is None:
            return v
        return CPSStringField.validate(self, v)

FieldRegistry.register(CPSAsciiStringOrNoneField)
