--------------------------------------------------
CPSForum README
--------------------------------------------------

:Author: Emmanuel Pietriga
:Address: ep@nuxeo.com
:Revision: $Id$

.. sectnum::    :depth: 4
.. contents::   :depth: 4


Introduction
============

CPSForum provides newsgroup-like discussion threads anywhere on
the site. It also makes it possible to make comments about
documents also organized by threads. See the 'Features' section
below for more information.


History & Bug fixes
===================

Important features and changes w.r.t CPSForum releases earlier
than 0.8.x:

- Posts are now searchable,

- Posts follow their own workflow (forum_post_wf) and have a
  publication status (see doc/forum_wf.svg for a graphical
  representation of this workflow),

- Comments are still stored in Forum objects, but there is no
  longer a comment_mode: standard forums are used in this context
  (some scripts differ slightly, but it is of no consequence to
  the user). This means that all standard forum features
  (moderation, notification, locking, etc.) are available in
  forums used for commenting documents,

- New permissions make it possible to fine tune who is allowed to
  do what on forums (see below for more information).

For history and bug fixes, please refer to the HISTORY file.


Installation
============

For installation information, please refer to the INSTALL file.

**Important note:** This version of CPSForum and all subsequent
versions based on CPSDocument posts are incompatible with existing
Forum instances that have been created with earlier versions of
CPSForum (i.e. which do not use CPSDocument posts). This means all
versions up to (and including) release 0.7.0-1 released in April
2004.


Features
========

Forum objects can be created in sections or workspaces.

- Forum settings

  + Moderation -- It is possible to assign moderators to any
    forum. There are two moderation modes:

    * 'a priori': messages posted have to be validated by a
      moderator to be visible by other users.

    * 'a posteriori': messages are published (and thus visible)
      directly after their posting.  Moderators can unpublish or
      delete them afterwards.

  + Anonymous posts: it is possible to allow anonymous users to
    post messages on a forum.

  + Locking mechanism: it is possible to lock a forum, making it
    read only. Locks can also be set at a finer grain (thread
    level: forbid new replies to a given thread)

  + Number of discussion threads per page: a maximum number of
    threads per page can be set. The value 0 means that there is
    no limit (all threads are displayed on the same page).

- Forum post handling

  Users allowed to post messages can create new discussion threads
  or answer to messages in other discussion threads.

  If the forum is moderated 'a priori', the message will appear in
  the thread with a red spot in front of it, meaning that other
  users cannot see it (moderators can of course see a pending
  message, as well as the user who created it).

  Users moderating the forum can publish this kind of messages,
  making them visible to all the other users in this forum.
  Moderators can also unpublish, or even delete messages.


Roles and permissions
=====================

Some details about roles and permissions associated with forums:

- There are three permissions associated with forums:

  + 'Forum Moderate': required to publish/unpublish/delete posts,

  + 'Forum Post': required to post new messages,

  + 'Forum manage comments': required to activate/deactivate
    comments about a given document.

- those three permissions are mapped to CPSDefault roles as follows:

  + Forum Moderate = WorkspaceManager, Section Manager, Section
    Reviewer, Owner

  + Forum Post = WorkspaceManager, WorkspaceMember,
    WorkspaceReader, SectionManager, SectionReviewer,
    SectionReader, Owner

  + Forum manage comments = WorkspaceManager, Section Manager,
    Section Reviewer, Owner

In addition, it is possible to assign roles ForumModerator and
ForumPoster (which speak for themselves) locally in a forum. It is
also possible to change default settings by using
``CPSInstaller.setupPortalPermissions()``.

Whatever their local roles/permissions on a given forum, users
need also to have standard permissions set on it (e.g. View). This
should be the case unless you have been making significant changes
to the default CPS role/permission mapping.


Discussions (comments about documents)
======================================

If your document is discussable (allow_discussion set to true), an
action in the action box makes it possible to activate comments
for your document. If comments are activated, a new action makes
it possible to actually comment the document. These comments are
managed by a CPSForum object (a forum is associated with each
document that contains comments).  Beware: the forum is associated
with the proxy document, not the actual document in the
repository, meaning that the forum is not shared by the various
versions of the document (published in sections, or workgroup
drafts). Forum objects themselves are stored in a specific
.cps_discussions folder in the parent folder of the document being
commented on (workspace or section) and are hidden from the user.

