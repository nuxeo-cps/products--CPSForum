##parameters=REQUEST=None

context.getContent().editForumProperties(**REQUEST.form)
if REQUEST.form.has_key('image_delete') and REQUEST.form['image_delete']:
    context.manage_delObjects(['image'])
elif REQUEST.form.has_key('image') and REQUEST.form['image']:
    if hasattr(context, 'image'):
        context.manage_delObjects(['image'])

    # TODO: why does it fail ?
    context.getContent().manage_addImage('image',REQUEST.form['image'])

context.REQUEST.RESPONSE.redirect(context.absolute_url()+"/view")

