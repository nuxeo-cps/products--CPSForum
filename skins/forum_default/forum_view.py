##parameters=post_id=None, REQUEST=None

# $Id$

"""Default view for the forum. If post_id is not None, post with id = <post_id>
will be displayed, otherwise first post will be displayed."""

if post_id is None:
    threads = context.getContent().getThreads()
    if len(threads) > 0:
        return context.forum_view_main(post_id=threads[0]['id'])

return context.forum_view_main()
