##parameters=post_id, is_reviewer=None

# $Id$

forum = context.getContent()
result = []
for root_post in forum.getThreads(proxy=context):
    result.append((root_post, forum.getDescendants(root_post['id'],
                                                   proxy=context)))

return context.forum_view_threads_main(post_id=post_id, descendants=result,
                                       is_reviewer=is_reviewer, forum=forum)
