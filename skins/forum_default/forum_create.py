##parameters=title, description, REQUEST=None

# FIXME: THIS NEED TO BE FIXED ONCE AND FOR ALL !
id = string.translate(title,string.maketrans(' .йиазкло','__eeaceei'))
if hasattr(context, id):
    # FIXME: What if this id is already taken too ?
    id += str(context.ZopeTime().millis())

context.invokeFactory("Forum", id, RESPONSE=None,
                      title=title, description=description) 

if REQUEST:
    REQUEST.RESPONSE.redirect(context.absolute_url() + "/" + id + "/view")

