from django.db import models
from django.contrib.auth.models import User
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.urls import reverse
from parler.models import TranslatableModel, TranslatedFields


def product_image_path(instance, filename):
    return f'products/{instance.name}/{filename}'


class SizeManager(models.Manager):
    def get_queryset(self):
        # Order sizes by numerical values
        return super().get_queryset().order_by(Cast('name', IntegerField()))


class Size(models.Model):
    name = models.CharField(max_length=10, unique=True)

    objects = SizeManager()

    # class Meta:
    #     ordering = ['name']

    def __str__(self):
        return str(self.name)


class Type(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=50),
        slug=models.SlugField(max_length=200, unique=True),
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_type', args=[self.slug])


class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=50),
        slug=models.SlugField(max_length=200, unique=True, blank=True),
    )
    class Meta:
        # ordering = ['name']
        # indexes = [
        #     models.Index(fields=['name']),
        # ]
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category',
                       args=[self.slug])


class Product(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        slug=models.SlugField(max_length=200),
        description=models.TextField(blank=True),
    )
    type = models.ForeignKey(Type, related_name='products', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    image = models.ImageField(upload_to=product_image_path)
    image_2 = models.ImageField(upload_to=product_image_path, blank=True)
    image_3 = models.ImageField(upload_to=product_image_path, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    size = models.ManyToManyField(Size)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ordering = ['name']
        indexes = [
        #    models.Index(fields=['id', 'slug']),
        #    models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.id, self.slug])


class Interaction(models.Model):
    product = models.ForeignKey(Product, related_name='interactions', on_delete=models.CASCADE)
    with_product = models.ForeignKey(Product, related_name='related_interactions', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 11)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}"

    @staticmethod
    def average_rating(product):
        reviews = Review.objects.filter(product=product)
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            return total_rating / reviews.count()
        return 0
