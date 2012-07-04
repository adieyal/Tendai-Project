import models

def menu(request):
    root_menu = models.MenuItem.objects.filter(parent=None, enabled=True)
    return { 'menu': root_menu }
