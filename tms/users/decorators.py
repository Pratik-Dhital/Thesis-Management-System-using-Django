from django.shortcuts import redirect

def student_required(view_func):

    def wrapper(request, *args, **kwargs):

        if request.user.role != 'student':
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper


def lecturer_required(view_func):

    def wrapper(request, *args, **kwargs):

        if request.user.role != 'lecturer':
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper