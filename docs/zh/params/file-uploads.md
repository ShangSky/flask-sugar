# 文件上传

`File` 用于定义客户端的上传文件。

## 导入 `File`

从 `flask_sugar` 导入 `File` 和 `UploadFile`：

```Python hl_lines="1"
from flask_sugar import Sugar, File, UploadFile

app = Sugar(__name__)


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    return {"filename": file.filename}
```

## 定义 `File` 参数

创建文件（`File`）参数的方式与 `Cookie` 和 `Header` 一样：

```Python hl_lines="7"
from flask_sugar import Sugar, File, UploadFile

app = Sugar(__name__)


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    return {"filename": file.filename}
```

## `UploadFile`

`UploadFile`是werkzeug.datastructures.FileStorage的别名, 它的属性如下:

* `filename`
* `name`
* `stream`
* `content_type`
* `content_length`
* `mimetype`
* `mimetype_params`
* `save(dst, buffer_size=16384)`
* `close()`

## 什么是 「表单数据」

与 JSON 不同，HTML 表单（`<form></form>`）向服务器发送数据通常使用「特殊」的编码。

**Flask Sugar** 要确保从正确的位置读取数据，而不是读取 JSON。

!!! note "技术细节"
    不包含文件时，表单数据一般用 `application/x-www-form-urlencoded`「媒体类型」编码。

    但表单包含文件时，编码为 `multipart/form-data`。使用了 `File`，**Flask Sugar** 就知道要从请求体的正确位置获取文件。
    
    编码和表单字段详见 <a href="https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Methods/POST" class="external-link" target="_blank"><abbr title="Mozilla Developer Network">MDN</abbr> Web 文档的 <code>POST </code></a> 小节。

!!! warning "警告"
    可在一个*路径操作*中声明多个 `File` 和 `Form` 参数，但不能同时声明要接收 JSON 的 `Body` 字段。因为此时请求体的编码是 `multipart/form-data`，不是 `application/json`。

    这不是 **Flask Sugar** 的问题，而是 HTTP 协议的规定。

## 多文件上传

Flask Sugar 支持同时上传多个文件。

可用同一个「表单字段」发送含多个文件的「表单数据」。

上传多个文件时，要声包含`UploadFile` 的列表（`List`）：

```Python hl_lines="9"
from typing import List

from flask_sugar import Sugar, File, UploadFile

app = Sugar(__name__)


@app.post("/upload")
def upload(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}
```

接收的也是含 `UploadFile` 的列表（`list`）。

## 小结

本节介绍了如何用 `File` 把上传文件声明为（表单数据的）输入参数。
