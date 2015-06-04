import math


def paginate(in_list, page, items_per_page):

    if items_per_page > 0:
        pages = int(math.ceil(float(len(in_list)) / items_per_page))
    else:
        pages = 1

    page = max(page, 1)
    page = min(page, pages)

    out = []

    if items_per_page > 0:
        from_index = (page - 1) * items_per_page
        to_index = min(len(in_list), page * items_per_page)
        out = in_list[from_index:to_index]

    return {
        'page': page,
        'pages': pages,
        'items_count': len(in_list),
    }, out