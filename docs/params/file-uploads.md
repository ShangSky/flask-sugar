# File Uploads

You can define files to be uploaded by the client using `File`.

## Import `File`

Import `File` and `UploadFile` from `flask_sugar`:

```Python hl_lines="1"
from flask_sugar import Sugar, File, UploadFile

app = Sugar(__name__)


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    return {"filename": file.filename}
```

## Define `File` parameters

Create file parameters the same way you would for `Cookie` or `Header`:

```Python hl_lines="7"
from flask_sugar import Sugar, File, UploadFile

app = Sugar(__name__)


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    return {"filename": file.filename}
```


## `UploadFile`

`UploadFile` is an alias to werkzeug.datastructures.FileStorage, it has the following attributes:

* `filename`
* `name`
* `stream`
* `content_type`
* `content_length`
* `mimetype`
* `mimetype_params`
* `save(dst, buffer_size=16384)`
* `close()`

## What is "Form Data"

The way HTML forms (`<form></form>`) sends the data to the server normally uses a "special" encoding for that data, it's different from JSON.

**Flask Sugar** will make sure to read that data from the right place instead of JSON.

!!! note "Technical Details"
    Data from forms is normally encoded using the "media type" `application/x-www-form-urlencoded` when it doesn't include files.

    But when the form includes files, it is encoded as `multipart/form-data`. If you use `File`, **Flask Sugar** will know it has to get the files from the correct part of the body.
    
    If you want to read more about these encodings and form fields, head to the <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST" class="external-link" target="_blank"><abbr title="Mozilla Developer Network">MDN</abbr> web docs for <code>POST</code></a>.

!!! warning
    You can declare multiple `File` and `Form` parameters in a *path operation*, but you can't also declare `Body` fields that you expect to receive as JSON, as the request will have the body encoded using `multipart/form-data` instead of `application/json`.

    This is not a limitation of **Flask Sugar**, it's part of the HTTP protocol.

## Multiple file uploads

It's possible to upload several files at the same time.

They would be associated to the same "form field" sent using "form data".

To use that, declare a `List` of `UploadFile`:

```Python hl_lines="9"
from typing import List

from flask_sugar import Sugar, File, UploadFile

app = Sugar(__name__)


@app.post("/upload")
def upload(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}
```

You will receive, as declared, a `list` of `UploadFile`s.

## Recap

Use `File` to declare files to be uploaded as input parameters (as form data).
