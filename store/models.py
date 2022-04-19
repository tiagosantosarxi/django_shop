from django.db import models
from django.urls import reverse
from category.models import Category


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    # FIXME this makes no sense we should not be deleting products
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name


class VariantManager(models.Manager):
    def colors(self):
        return super(VariantManager, self).filter(variant_category='color', is_active=True)

    def sizes(self):
        return super(VariantManager, self).filter(variant_category='size', is_active=True)


variant_category_choise = (
    ('color', 'color'),
    ('size', 'size')
)


class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant_category = models.CharField(max_length=100, choices=variant_category_choise)
    variant_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = VariantManager()

    def __str__(self):
        return self.variant_value
