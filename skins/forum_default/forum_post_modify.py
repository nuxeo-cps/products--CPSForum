##parameters=parent_id=None, frm_start=None, REQUEST=None
# $Id$

# parent_id is actually the post_id (called parent because same param
# is used in forum_post_reply)

if REQUEST is not None:
    url = "%s/%s/cpsdocument_edit_form" % (context.absolute_url(),
                                           parent_id)
    REQUEST.RESPONSE.redirect(url)
