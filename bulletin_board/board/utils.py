menu = [{'title' : 'Bulletin Board', 'URL' : 'main'},
        {'title' : 'О сайте', 'URL' : 'about'},
        {'title' : 'Создать объявление', 'URL' : 'create_event'},
        {'title' : 'Найти объявление', 'URL' : 'search_event'},
        {'title' : 'Найти автора', 'URL' : 'search_player'},
        {'title' : 'Войти', 'URL' : 'login'},
        {'title' : 'Создать профиль', 'URL' : 'create profile'}]


class DataMixin:
    def get_mixin_objects(self, context, **kwargs):
        context['menu'] = menu
        context.update(kwargs)
        return context