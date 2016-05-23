===============================
Swagger Fuzzer
===============================

Swagger Fuzzer helps you do fuzzing testing on your Swagger APIs.

* Free software: MIT License
* Documentation: https://swagger_fuzzer.readthedocs.org.

Usage
-----

Install swagger-fuzzer via pip:

.. code:: shell

    pip install https://github.com/Lothiraldan/swagger-fuzzer/archive/master.zip

Point it to your swagger specification:

.. code:: shell

    swagger-fuzzer http://localhost:80/v2/swagger.json

If swagger-fuzzer find any problem, it will print you a report, for example:

.. code:: shell

    Falsifying example: swagger_fuzzer(data=request(...))
    Curl command: curl -i -X GET -d '' 'http://localhost/pet/findByStatus'
    Traceback (most recent call last):
      File "/Users/lothiraldan/.virtualenvs/swagger-fuzzer/bin/swagger-fuzzer", line 9, in <module>
        load_entry_point('swagger-fuzzer', 'console_scripts', 'swagger-fuzzer')()
      File "/Users/lothiraldan/projects/swagger-fuzzer/swagger_fuzzer/swagger_fuzzer/swagger_fuzzer.py", line 34, in main
        do(args)
      File "/Users/lothiraldan/projects/swagger-fuzzer/swagger_fuzzer/swagger_fuzzer/swagger_fuzzer.py", line 79, in do
        swagger_fuzzer()
      File "/Users/lothiraldan/projects/swagger-fuzzer/swagger_fuzzer/swagger_fuzzer/swagger_fuzzer.py", line 68, in swagger_fuzzer
        @hsettings(max_examples=settings.iterations)
      File "/Users/lothiraldan/projects/swagger-fuzzer/hypothesis-python/src/hypothesis/core.py", line 541, in wrapped_test
        print_example=True, is_final=True
      File "/Users/lothiraldan/projects/swagger-fuzzer/hypothesis-python/src/hypothesis/executors.py", line 58, in default_new_style_executor
        return function(data)
      File "/Users/lothiraldan/projects/swagger-fuzzer/hypothesis-python/src/hypothesis/core.py", line 104, in run
        return test(*args, **kwargs)
      File "/Users/lothiraldan/projects/swagger-fuzzer/swagger_fuzzer/swagger_fuzzer/swagger_fuzzer.py", line 76, in swagger_fuzzer
        validator(SPEC, request, result, settings)
      File "/Users/lothiraldan/projects/swagger-fuzzer/swagger_fuzzer/swagger_fuzzer/validators.py", line 54, in valid_output_mime
        raise AssertionError("Response content-type {} is not declared: {}".format(response.headers['Content-Type'], valids))
    AssertionError: Response content-type text/html; charset=ISO-8859-1 is not declared: []

Bugs hunted
-----------

Swagger-fuzzer really find bugs, here is a non-extensive list of bugs found with swagger-fuzzer:

* https://github.com/pallets/flask/issues/1761, null byte filename crash flask file handling code.

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

This project was sponsored by my employer Sqreen_ and developed initially for our needs.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _Sqreen: https://www.sqreen.io
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
