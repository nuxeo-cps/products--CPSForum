##parameters=post_id, action, mode

#mode is '0' for standard forums, '1' for comments

session_data = context.session_data_manager.getSessionData()
session_data.set('post_' + str(post_id), action)

if mode == '1':
    #in this case, context is a CPSDocument
    return context.cpsdocument_view()
else :
    #in this case, context is a Forum
    return context.forum_view_main()
