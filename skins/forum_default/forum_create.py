##parameters=title, description, REQUEST=None

id = string.translate(title,string.maketrans(' .йиазкло','__eeaceei'))
if hasattr(context, id):
    id += str(context.ZopeTime().millis())

context.invokeFactory("Forum",id, RESPONSE=None,title=title,description=description) 
REQUEST.RESPONSE.redirect(context.absolute_url()+"/"+id+"/view")

