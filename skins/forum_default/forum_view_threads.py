##parameters=post_id, is_reviewer=None

# $Id$

forum = context.getContent()
result = []
for thread_info in forum.getThreads():
    result.append((thread_info, forum.getDescendants(thread_info['id']),))

return context.forum_view_threads_main(
    post_id=post_id, descendants=result, is_reviewer=is_reviewer, 
    comment_mode=0, forum=forum)
