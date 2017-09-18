from django.http import HttpResponse
import StringIO
import zipfile


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


def multiple_files_to_zip_httpresponse(files, zip_filename):
    '''
    return a HttpResponse with multiple files in zip format
    :param files: dict with {document_filename: data}
    :param zip_filename: string as 'zip_filename'
    '''
    outfile = StringIO.StringIO()
    with zipfile.ZipFile(outfile, 'w') as zf:
        for k, v in files.items():
            zf.writestr(k, v)
    
    response = HttpResponse(outfile.getvalue(), content_type="application/octet-stream")
    response['Content-Disposition'] = 'attachment; filename={}.zip'.format(zip_filename)
    return response