##parameters=post_id, action, mode

# $Id$

# Mode is '0' for standard forums, '1' for comments.
# XXX: that's not explicit enough. And what if we want to add comments on
# something else than CPSDocuments ?

session_data = context.session_data_manager.getSessionData()
session_data.set('post_' + str(post_id), action)

if mode == '1':
    # In this case, context is a CPSDocument
    return context.cpsdocument_view()
else :
    # In this case, context is a Forum
    return context.forum_view_main()
