
  ---
  ### python
    - [PyYAML Documentation](http://pyyaml.org/wiki/PyYAMLDocumentation)
    - [Flask](http://flask.pocoo.org/docs/0.12/api/)
    - [Flask-RESTful](http://flask-restful.readthedocs.io/en/0.3.6/api.html)
    - [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.3/api/)
    - [MarshMallow](http://marshmallow.readthedocs.io/en/latest/quickstart.html)
    - [Scapy](http://secdev.org/projects/scapy/demo.html)
    - [Pandas](http://pandas.pydata.org/pandas-docs/version/0.20/io.html)
    - [Numpy](https://docs.scipy.org/doc/numpy/user/quickstart.html)
    - [Tensorflow Install](https://blog.csdn.net/u014797226/article/details/80229887)
    - [Tensorflow Install2](https://www.cnblogs.com/Ph-one/p/9000211.html)

  ---
  ### database
    - [Redis](https://www.fullstackpython.com/blog/install-redis-use-python-3-ubuntu-1604.html)
    - [Peewee](http://docs.peewee-orm.com/en/latest/peewee/example.html)
    - [alembic](http://alembic.zzzcomputing.com/en/latest/tutorial.html#the-migration-environment)
  ---

  ### other
    - [Unicode Characters](http://graphemica.com/unicode/characters)
    - [About redis-cli](http://blog.fens.me/linux-redis-install/)
    - chrome install third party plug-ins `google-chrome --enable-easy-off-store-extension-install`
    - [chromedriver](http://chromedriver.storage.googleapis.com/index.html)

  ### [APIcode](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html)
      200 OK                    [GET]             服务器成功返回用户请求的数据
      201 CREATED               [POST/PUT/PATCH]  用户新建或修改数据成功
      202 Accepted              [*]               表示一个请求已经进入后台排队
      204 NO CONTENT            [DELETE]          用户删除数据成功
      400 INVALID REQUEST       [POST/PUT/PATCH]  用户发出的请求错误
      401 Unauthorized          [*]               用户无权限
      403 Forbidden             [*]               禁止访问（有权限）
      404 NOT FOUND             [*]               服务器地址不存在
      406 Not Acceptable        [GET]             用户请求的格式不可得
      410 Gone                  [GET]             服务器资源不存在
      412 Precondition failed   [POST/GET]        未满足'先决条件', 一般是cookie
      422 Unprocesable entity   [POST/PUT/PATCH]  创建对象验证错误
      429 Too Many Requests     [*]               太多请求
      500 INTERNAL SERVER ERROR [*]               服务器内部错误