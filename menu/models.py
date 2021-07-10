import calendar
import datetime
import unidecode
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify


class Category(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=1000)
    slug = models.SlugField(max_length=30, unique=True,
                            default="", blank=True, null=True)

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    title = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=30, unique=True,
                            default="", blank=True, null=True)

    def __str__(self):
        return self.title


class Dish(models.Model):
    title = models.CharField(max_length=60)
    calories = models.PositiveIntegerField(default=0)
    meal_of_the_day = models.PositiveIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)])
    slug = models.SlugField(max_length=60, unique=True,
                            default="", blank=True, null=True)

    ingredients = models.ManyToManyField(Ingredient, blank=True)

    def __str__(self):
        return self.title


class DailyMeal(models.Model):
    title = models.CharField(default="", max_length=100)

    dish_1 = models.ForeignKey(Dish, blank=True, null=True, on_delete=models.SET_NULL,
                               related_name='breakfast', verbose_name='breakfast')
    dish_2 = models.ForeignKey(Dish, blank=True, null=True, on_delete=models.SET_NULL,
                               related_name='brunch', verbose_name='brunch')
    dish_3 = models.ForeignKey(Dish, blank=True, null=True, on_delete=models.SET_NULL,
                               related_name='lunch', verbose_name='lunch')
    dish_4 = models.ForeignKey(Dish, blank=True, null=True, on_delete=models.SET_NULL,
                               related_name='dinner', verbose_name='dinner')
    dish_5 = models.ForeignKey(Dish, blank=True, null=True, on_delete=models.SET_NULL,
                               related_name='supper', verbose_name='supper')

    calories = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    @property
    def get_all_dishes(self):
        dishes = [self.dish_1, self.dish_2,
                  self.dish_3, self.dish_4, self.dish_5]
        return dishes


class Menu(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=1000)
    calories_daily = models.PositiveIntegerField(default=0, verbose_name='Calories average')
    slug = models.SlugField(max_length=30, unique=True,
                            default="", blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, blank=True)

    price_custom = models.BooleanField(default=False)
    price_daily = models.DecimalField(default=0, max_digits=5,
                                      decimal_places=2, verbose_name='Daily costs')
    price_weekly = models.DecimalField(default=0, max_digits=7,
                                       decimal_places=2, verbose_name='Weekly costs')
    price_monthly = models.DecimalField(default=0, max_digits=10,
                                        decimal_places=2, verbose_name='Monthly costs')

    day_1 = models.ForeignKey(DailyMeal, on_delete=models.CASCADE,
                              related_name="monday", verbose_name='monday')
    day_2 = models.ForeignKey(DailyMeal, on_delete=models.CASCADE,
                              related_name="tuesday", verbose_name="tuesday")
    day_3 = models.ForeignKey(DailyMeal, on_delete=models.CASCADE,
                              related_name="wednesday", verbose_name="wednesday")
    day_4 = models.ForeignKey(DailyMeal, on_delete=models.CASCADE,
                              related_name="thursday", verbose_name="thursday")
    day_5 = models.ForeignKey(DailyMeal, on_delete=models.CASCADE,
                              related_name="friday", verbose_name="friday")
    day_6 = models.ForeignKey(DailyMeal, on_delete=models.CASCADE,
                              related_name="saturday", verbose_name="saturday")
    day_7 = models.ForeignKey(DailyMeal, on_delete=models.CASCADE,
                              related_name="sunday", verbose_name="sunday")

    def __str__(self):
        return self.title

    @property
    def get_all_days(self):
        days = [self.day_1, self.day_2, self.day_3,
                self.day_4, self.day_5, self.day_6, self.day_7]
        return days


@receiver(pre_save, sender=Category)
def pre_save_ingredient(sender, instance, *args, **kwargs):
    instance.slug = slugify(unidecode.unidecode(instance.title))


@receiver(pre_save, sender=Ingredient)
def pre_save_ingredient(sender, instance, *args, **kwargs):
    instance.slug = slugify(unidecode.unidecode(instance.title))


@receiver(pre_save, sender=Dish)
def pre_save_dish(sender, instance, *args, **kwargs):
    instance.slug = slugify(unidecode.unidecode(instance.title))


@receiver(pre_save, sender=DailyMeal)
def pre_save_daily_meal(sender, instance, *args, **kwargs):
    calories = [instance.dish_1.calories,
                instance.dish_2.calories,
                instance.dish_3.calories,
                instance.dish_4.calories,
                instance.dish_5.calories]
    instance.calories = sum(calories)


@receiver(pre_save, sender=Menu)
def pre_save_dish(sender, instance, *args, **kwargs):
    instance.slug = slugify(unidecode.unidecode(instance.title))
    if not instance.price_custom:
        instance.price_weekly = instance.price_daily * 7
        #        now = datetime.datetime.now()
        #        days_in_month = calendar.monthrange(now.year, now.month)[1]
        instance.price_monthly = instance.price_daily * 30

    instance.calories_daily = round(sum(day.calories for day in instance.get_all_days) / 7)
