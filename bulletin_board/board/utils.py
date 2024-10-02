menu = [{'title' : 'Bulletin Board', 'URL' : 'main'},
        {'title' : 'О сайте', 'URL' : 'about'},
        {'title' : 'Создать объявление', 'URL' : 'create_event'},
        {'title' : 'Найти объявление', 'URL' : 'search_event'},
        {'title' : 'Найти автора', 'URL' : 'search_player'},
        {'title' : 'Создать профиль', 'URL' : 'create profile'},
        {'title' : 'Войти', 'URL' : 'users:login'},]


class DataMixin:
    paginate_by = 3

    def get_mixin_objects(self, context, **kwargs):
        context.update(kwargs)
        return context