##parameters=post_id, action

# $Id$

session_data = context.session_data_manager.getSessionData()
session_data.set('post_' + str(post_id), action)

return context.forum_view_main()
