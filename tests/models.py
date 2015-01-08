from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from reviews.models import Review, Reviewable

class Product(Reviewable):
    name = models.CharField(max_length=40, unique=True)

    reviews = GenericRelation(Review, related_query_name="products")

    def __unicode__(self):
        return self.name
