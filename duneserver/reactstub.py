
def reactstub(title, stylesheets=[], scripts=[], bootstrap="{}", copyright="© Evan F Lynch 2017"):
    css = map(lambda s: '<link rel="stylesheet" type="text/css" href="/static/{}">'.format(s), stylesheets)
    js = map(lambda s: '<script src="/static/{}"></script>'.format(s), scripts)
    return """
<!-- HTML stub that loads ReactJS -->
<!-- {} -->
<head>
    <title>{}</title>
    <meta charset="UTF-8">
    <script>window.bootstrap = JSON.parse('{}'); </script>
    {}
    {}
</head>
<body>
    <div id="header"></div>
    <div id="content"></div>
</body>
""".format(copyright, title, bootstrap, "\n".join(css), "\n".join(js))
