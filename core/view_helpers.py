from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import ProtectedError
from django.shortcuts import redirect, render


def render_model_form(request, form, title, cancel_url, **extra):
    ctx = {
        'form': form,
        'title': title,
        'cancel_url': cancel_url,
        'cascade_form': extra.pop('cascade_form', False),
        'multipart': extra.pop('multipart', False),
    }
    ctx.update(extra)
    return render(request, 'form.html', ctx)


def paginate(request, queryset, per_page=12):
    """Return a Page object for the given queryset using the ?page= query param."""
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get('page'))


def confirm_delete(request, obj, label, cancel_url, success_message=None):
    """Render a shared delete-confirmation page and delete on POST.

    Returns a redirect to cancel_url on success, otherwise the confirm page.
    """
    if request.method == 'POST':
        try:
            obj.delete()
        except ProtectedError:
            messages.error(
                request,
                f'Cannot delete this {label.lower()} because other records '
                f'(e.g. enrollments or fees) still reference it. Remove those first.',
            )
            return redirect(cancel_url)
        messages.success(request, success_message or f'{label} deleted.')
        return redirect(cancel_url)
    return render(request, 'confirm_delete.html', {
        'label': label,
        'object_str': str(obj),
        'cancel_url': cancel_url,
    })
