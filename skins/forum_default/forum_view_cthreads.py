##parameters=post_id, forum_proxy, forum

# $Id$


result = []
for root_post in forum.getThreads(proxy=forum_proxy):
    result.append((root_post, forum.getDescendants(root_post['id'],
                                                   proxy=forum_proxy)))

return context.forum_view_threads_main(post_id=post_id, descendants=result,
                                       is_reviewer=0, forum=forum)
