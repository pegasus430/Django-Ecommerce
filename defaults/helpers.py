def get_model_fields(model, include_id_field=False):
    ''' returns a list of all fieldnames of your model. 
    By default, it excludes the autofield id'''
    fields = []
    for f in model._meta.fields:
        fieldname = f.attname
        if fieldname == 'id' and not include_id_field:
            pass
        else:
            fields.append(f.attname)
    return fields
