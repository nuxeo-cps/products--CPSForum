##parameters=post_id, is_reviewer=None

# $Id$

forum = context.getContent()

try:
    session_data = context.session_data_manager.getSessionData()
    sort_by = session_data.get('frm_sort', None)
except AttributeError:
    sort_by = None

if forum.tree_display != 'title' or (sort_by is not None and sort_by != 'threads'):
    post_proxies = context.objectValues(['CPS Proxy Document'])
    result = [forum.getPostInfo(proxy) for proxy in post_proxies]
else:
    result = []
    for root_post in forum.getThreads(proxy=context):
        result.append((root_post, forum.getDescendants(root_post['id'],
                                                       proxy=context)))
    
return context.forum_view_threads_main(post_id=post_id, descendants=result,
                                       is_reviewer=is_reviewer, forum=forum,
                                       sort_by=sort_by,
                                       display_mode=forum.tree_display)

