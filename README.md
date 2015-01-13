# django-reviews

A simple to use framework for user submitted reviews of objects.



## Getting Started

Imagine the use case of a web store. Users (`django.contrib.auth.User`) can submit reviews for Products (`store.models.Product`), making `Product` the subclass of `reviews.models.Reviewable`. Here's how to create a simple store application using the django-reviews framework.

1.  Install django-reviews from GitHub using pip:

    `pip install git+ssh://git@github.com/atheiman/django-reviews.git@1.0.0#egg=reviews`

1.  Add `reviews` to `INSTALLED_APPS` in your settings file. Be sure [`django.contrib.auth`](https://docs.djangoproject.com/en/1.7/ref/contrib/auth/) and [`django.contrib.contenttypes`](https://docs.djangoproject.com/en/1.7/ref/contrib/contenttypes/) are there too (in a default django project creation, they should be there).

    ```python
    INSTALLED_APPS = (
        # ...
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'reviews',
        'store',       # our app included for this example
        # ...
    )
    ```

1.  Also in your settings file, create an empty `DJANGO_REVIEWS` dictionary. This dictionary will be used to configure django-reviews. Lets go ahead and add one key to the dictionary, `REVIEWABLE_MODELS`. The `REVIEWABLE_MODELS` key is used to register models that you want to define as reviewable. It accepts an iterable of dictionary elements containing 2 required keys:

    ```python
    DJANGO_REVIEWS = {}
    DJANGO_REVIEWS['REVIEWABLE_MODELS'] = [
        {
            'app_label': 'store',
            'model': 'product',
        },
    ]
    ```

    > **Note**<br>
    > Defining the `DJANGO_REVIEWS` dict for configuration is not _required_, but it is recommended that you do so and define at least the recommended models as described in the [Configuration section below](#configuration).

1.  In the store app's `models.py` import the necessary classes and create the `Product` model from the `Reviewable` base class:

    ```python
    from django.db import models
    from django.contrib.contenttypes.fields import GenericRelation
    from reviews.models import Review, Reviewable

    class Product(Reviewable):
        name = models.CharField(max_length=40)

        # ...

        reviews = GenericRelation(Review, related_query_name="products")

        def __unicode__(self):
            return self.name
    ```



## Basic Model Usage

Create reviews with `Review.objects.create()`:

```python
>>> from reviews.models import Review
>>> from django.contrib.auth.models import User
>>> from simple_app.models import Product
>>>
>>> user = User.objects.create_user(username='joetest')
>>> product = Product.objects.create(name='22-inch TV')
>>> review = Review.objects.create(
...   reviewed_object = product,
...   user = user,
...   score = 3,
...   comment = "I like this tv a lot, I would buy it again.",
... )
```

Simple lookups across the relationships:

```python
>>> user.reviews.all()
[<Review: object: 22-inch TV, score: 3, user: joetest>]
>>> product.reviews.all()
[<Review: object: 22-inch TV, score: 3, user: joetest>]
```

Reverse lookups from the `Review` table as well:

```python
>>> Review.objects.filter(products__name__contains='tv')
[<Review: object: 22-inch TV, score: 3, user: joetest>]
>>> Review.objects.filter(user__username__contains='joe')
[<Review: object: 22-inch TV, score: 3, user: joetest>]
```

Extra functions built into `Reviewable` abstract base model:

```python
>>> user_2 = User.objects.create_user(username='atheiman')
>>> review_2 = Review.objects.create(
...   reviewed_object = product,
...   user = user_2,
...   score = 4,
...   comment = "This is an outstanding television!",
... )
>>> product.avg_review_score()
Decimal('3.5')
```

Functionality available in `Review`:

```python
>>> review.is_updated()    # returns False if no updates
False
>>> review.score = 1
>>> review.comment = "After using the tv for more than 10 seconds, it broke."
>>> review.save()
>>> review.is_updated()    # returns updated datetime if updated
datetime.datetime(2015, 1, 7, 19, 20, 15, 723908, tzinfo=<UTC>)
```



## Configuration

You can configure django-reviews in your django settings. Create a `DJANGO_REVIEWS` dictionary in your settings file, and add settings keys and values as you prefer. Generally the defaults are created from how [Amazon.com](http://www.amazon.com/) implements reviews. Below are all the available settings, their defaults, and a brief explanation.

| Setting Key                  | Default | Notes                                            |
| :--------------------------- | :------ | :----------------------------------------------- |
| `REVIEWABLE_MODELS`          | `None`  | **Recommended**. List of dictionaries describing reviewable models. Each element of `REVIEWABLE_MODELS` must be a dictionary containing the keys `app_label` and `model` with string values. The string values are equivalent to what is stored in the `ContentType` model instance for the models. The `app_label` is generally the lowercased name of the app the model is defined in, and the `model` string is generally the lowercased name of the model. In the store example above, the `REVIEWABLE_MODELS` list would be `[{'app_label': 'store', 'model': 'product'}]`. |
| `MAX_SCORE`                  | `5`     | Maximum value of `Review.score`.                 |
| `MIN_SCORE`                  | `1`     | Minimum value of `Review.score`.                 |
| `SCORE_CHOICES`              | `zip(range(MIN_SCORE, MAX_SCORE + 1),range(MIN_SCORE, MAX_SCORE + 1))` | List of tuple pairs to be used as a [`choices`](https://docs.djangoproject.com/en/1.7/ref/models/fields/#choices) list of acceptable `Review.score` values. The default evaluates to `[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]` (accepts user input of integers between 1 and 5) if `MIN_SCORE` and `MAX_SCORE` have not been changed. Otherwise it will generate a list of choices as integers from `MIN_SCORE` to `MAX_SCORE`. |
| `MAX_COMMENT_LENGTH`         | `1000`  | Maximum length of `Review.comment` [`TextField`](https://docs.djangoproject.com/en/1.7/ref/models/fields/#textfield). |
| `UPDATED_COMPARISON_SECONDS` | `10`    | Number of seconds required to pass before changes to any `Review` fields cause `Review.is_updated()` to return the `Review.update` `datetime` instance. If the number of seconds has not passed, the `Review.is_updated()` method returns `False`. |
| `AVG_SCORE_DIGITS`           | `2`     | Number of digits in the [`Decimal`](https://docs.python.org/2/library/decimal.html) instance returned by `Review.avg_review_score()`. |
| `COMMENT_REQUIRED`           | `False` | If `True`, `Review.comment` [`TextField`](https://docs.djangoproject.com/en/1.7/ref/models/fields/#textfield) will be required. |
| `COMMENT_APPROVAL_REQUIRED`  | `False` | If `True`, `Review.comment_approved` will be `False` by default. You could use this to render a review without its comment until a staff member has approved the comment. |

> **Note**<br>
> Other configuration could easily be done by subclassing either `reviews.models.Review` or `reviews.models.Reviewable` before using them.



## More Info

The `Review` model is not all that complex. To see all available fields for the model, simply [browse the code](https://github.com/atheiman/django-reviews/blob/master/reviews/models.py).



## Testing

```shell
$ ./runtests.py
```
