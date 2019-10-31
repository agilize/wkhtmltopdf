#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    WSGI APP to convert wkhtmltopdf As a webservice
    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import json
import tempfile
import zipfile
from werkzeug.wsgi import wrap_file
from werkzeug.wrappers import Request, Response
from executor import execute, ExternalCommandFailed


@Request.application
def application(request):
    """
    To use this application, the user must send a POST request with
    base64 or form encoded encoded HTML content and the wkhtmltopdf Options in
    request data, with keys 'base64_html' and 'options'.
    The application will return a response with the PDF file.
    """
    if request.method != 'POST':
        return Response('alive')

    with tempfile.NamedTemporaryFile(suffix='.zip') as source_file:
        source_file.write(request.files['file'].read())
        options = json.loads(request.form.get('options', '{}'))

        source_file.flush()

        with tempfile.TemporaryDirectory() as tmpdirname:
            with zipfile.ZipFile(source_file.name, 'r') as zip_ref:
                zip_ref.extractall(tmpdirname)

                args = ['wkhtmltopdf']

                if options:
                    for option, value in options.items():
                        if option.isupper():
                            args.append('-%s' % option)
                        else:
                            args.append('--%s' % option)

                        if value:
                            if value.isdigit():
                                args.append('%s' % value)
                            else:
                                args.append('"%s"' % value)

                file_name = tmpdirname + '/index.html'
                args += [file_name, file_name + ".pdf"]

                cmd = ' '.join(args)

                try:
                    execute(cmd)
                except ExternalCommandFailed as e:
                    # | EditCode | Explanation                                                   |
                    # | 0        | All OK                                                        |
                    # | 1        | PDF generated OK, but some request(s) did not return HTTP 200 |
                    # | 2        | Could not something something                                 |
                    # | X        | Could not write PDF: File in use                              |
                    # | Y        | Could not write PDF: No write permission                      |
                    # | Z        | PDF generated OK, but some JavaScript requests(s) timeouted   |
                    # | A        | Invalid arguments provided                                    |
                    # | B        | Could not find input file(s)                                  |
                    # | C        | Process timeout                                               |
                    if e.returncode not in [0, 1]:
                        raise e

                pdf_file = open(file_name + '.pdf')

                return Response(
                    wrap_file(request.environ, pdf_file),
                    mimetype='application/pdf',
                    direct_passthrough=True,
                )


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple(
        '127.0.0.1', 5000, application, use_debugger=True, use_reloader=True
    )
