# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Emmanuel Pietriga <ep@nuxeo.com>
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
"""CPS Forum permissions.

  - 'Forum Post' is the permission needed to post a message to a forum

  - 'Forum Moderate' is the permission needed to moderate a forum

  - 'Forum manage comments' is the permission needed to manage document
    comments (stored in forum objects)

"""

from Products.CMFCore.permissions import setDefaultRoles

ForumPost = 'Forum Post'
setDefaultRoles(ForumPost, ('Manager', 'Owner'))

ForumModerate = 'Forum Moderate'
setDefaultRoles(ForumModerate, ('Manager', 'Owner'))

ForumManageComments = 'Forum manage comments'
setDefaultRoles(ForumManageComments, ('Manager', 'Owner'))

