## Script (Python) "forum_view"
##parameters=post_id=None, REQUEST=None
# $id:$

""" """

if post_id is None:
    threads = context.getContent().getThreads()
    if len(threads) > 0:
        return context.forum_view_main(post_id=threads[0]['id'])

return context.forum_view_main()
