swagger_template: str = """
<!DOCTYPE html>
<html>

<head>
    <link type="text/css" rel="stylesheet" href="{{ swagger_css_url }}">
    <title>{{ title }}</title>
</head>

<body>
    <div id="swagger-ui">
    </div>
    <script src="{{ swagger_js_url }}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
        const ui = SwaggerUIBundle({
            url: "{{ openapi_json_url }}",
            dom_id: '#swagger-ui',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout",
            deepLinking: true,
            showExtensions: true,
            showCommonExtensions: true
        })
    </script>
</body>

</html>
"""
redoc_template: str = """
<!DOCTYPE html>
<html>

<head>
    <title>{{ title }}</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <!--
    ReDoc doesn't change outer page styles
    -->
    <style>
        body {
            margin: 0;
            padding: 0;
        }
    </style>
</head>

<body>
    <redoc spec-url="{{ openapi_json_url }}"></redoc>
    <script src="{{ redoc_js_url }}"> </script>
</body>

</html>
"""
