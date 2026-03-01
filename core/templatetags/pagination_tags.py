from django import template

register = template.Library()


@register.simple_tag
def pagination_range(page_obj, window=2):
    """Return a compact page range list for pagination display.

    Example output with many pages: [1, '...', 4, 5, 6, '...', 20]
    """
    try:
        total = page_obj.paginator.num_pages
        current = page_obj.number
    except Exception:
        return []

    window = int(window)
    start = max(1, current - window)
    end = min(total, current + window)

    pages = []
    if start > 1:
        pages.append(1)
        if start > 2:
            pages.append('...')

    for i in range(start, end + 1):
        pages.append(i)

    if end < total:
        if end < total - 1:
            pages.append('...')
        pages.append(total)

    return pages
