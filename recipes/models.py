from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        constraints = [models.UniqueConstraint(
            fields=['name', 'hex_style', 'slug'], name='unique_tag'
            )]

    name = models.CharField(verbose_name='Название тэга', max_length=50)
    slug = models.SlugField(verbose_name='Слаг тэга', max_length=20,
                            db_index=True)
    hex_style = models.CharField(verbose_name='Цвет тега', max_length=20)

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        db_index=True
    )
    unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=20
    )

    def __str__(self):
        return self.name



class Recipe(models.Model):

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    author = models.ForeignKey(User, verbose_name='Автор рецепта',
                               related_name='recipe_authors',
                               on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Название рецепта', max_length=200,
                            blank=False)
    image = models.ImageField(verbose_name='Изображение', upload_to='recipes/', blank= True)
    description = models.TextField(verbose_name='Описание рецепта',
                                   max_length=1000,
                                   blank=True)
    ingredients = models.ManyToManyField(Ingredient,
                                         verbose_name='Ингредиенты',
                                         related_name='recipe_ingredients',
                                         through='Amount',
                                         through_fields=('recipe', 'ingredient')
                                         )
    cook_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='в минутах',
        null=True,
    )
    pub_date = models.DateField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    tag = models.ManyToManyField(Tag, verbose_name='Тэг', related_name='recipe_tags')

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url



class Amount(models.Model):

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='amount_recipes'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    units = models.PositiveIntegerField(
        verbose_name='Количество/объем',
        default=0,
    )

    def __str__(self):
        return str(self.units)