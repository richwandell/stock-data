from rest_framework.exceptions import ValidationError


def post_json_not_empty(fields):

    fields = fields if len(fields) > 0 else []

    def decorator(func):

        def new_func(request):
            try:
                for field in fields:
                    assert field in request.data, field
                    assert request.data[field].strip() != '', field
            except AssertionError as e:
                raise ValidationError(detail=str(e))
            return func(request)
        return new_func
    return decorator