from category.models import Category


def menu_links(req):
    links  = Category.objects.all()
    return dict(links=links)