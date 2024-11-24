from django.http import JsonResponse


def not_allowed_error():
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def method_decorator(f, method):
    def decorated(request, *args, **kwargs):
        if request.method != method:
            return not_allowed_error()
        return f(request, *args, **kwargs)

    return decorated


def get_method(function):
    return method_decorator(function, "GET")


def post_method(function):
    return method_decorator(function, "POST")


def put_method(function):
    return method_decorator(function, "PUT")


def delete_method(function):
    return method_decorator(function, "DELETE")