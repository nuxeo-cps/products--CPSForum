##parameters=post_id, is_reviewer=None

# $Id$

doc = context.getContent()
result = []
for i in doc.getThreads():
    result.append((i, doc.getDescendants(i['id']),))

return context.forum_view_threads_main(post_id=post_id, descendants=result, 
                                       is_reviewer=is_reviewer, comment_mode=0,
                                       forum=doc)
