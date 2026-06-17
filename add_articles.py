import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')
django.setup()

from shop.models import Article

articles = [
    {
        'title': 'Петли и оттяжки: что нужно знать новичку',
        'slug': 'petli-i-ottyazhki-dlya-novichkov',
        'excerpt': 'Разбираемся, какие оттяжки выбрать для первого маршрута.',
        'content': 'Когда вы только начинаете заниматься скалолазанием...',
        'author': 'Альпинистский гид',
    },
    {
        'title': 'Выбираем первую каску для альпинизма',
        'slug': 'kak-vybrat-kasku-dlya-alpinizma',
        'excerpt': 'Рассказываем о типах касок, материалах и на что обратить внимание.',
        'content': 'Каска — это не просто аксессуар, а важнейший элемент безопасности...',
        'author': 'Школа альпинизма',
    },
    # Добавь остальные статьи по тому же принципу
]

for article_data in articles:
    obj, created = Article.objects.get_or_create(
        slug=article_data['slug'],
        defaults=article_data
    )
    if created:
        print(f'✅ Добавлена: {article_data["title"]}')
    else:
        print(f'⏩ Уже есть: {article_data["title"]}')