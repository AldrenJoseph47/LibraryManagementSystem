from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


class Plan(models.Model):
    PLAN_CHOICES = [
        ('Quarterly Plan', 'Quarterly Plan'),
        ('Half-yearly Plan', 'Half-yearly Plan'),
        ('Annual Plan', 'Annual Plan'),
    ]

    plan_name = models.CharField(max_length=20, choices=PLAN_CHOICES)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.CharField(max_length=200)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            if self.plan_name == 'Quarterly Plan':
                self.end_date = self.start_date + timedelta(days=90)
            elif self.plan_name == 'Half-yearly Plan':
                self.end_date = self.start_date + timedelta(days=180)
            elif self.plan_name == 'Annual Plan':
                self.end_date = self.start_date + timedelta(days=365)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.plan_name


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)


class Genre(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='authors/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ratings = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)

    def __str__(self):
        return self.title


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback = models.TextField(max_length=250)
    response = models.TextField(max_length=250, blank=True, default="Not yet responded")

    def __str__(self):
        return f"Feedback by {self.user.username}"

    def is_responded(self):
        return bool(self.response.strip())


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_for = models.CharField(max_length=30)
    mode_of_payment = models.CharField(max_length=30)
    date_and_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment for {self.payment_for} by {self.user}'


class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rental_start_date = models.DateField(auto_now_add=True)
    rental_end_date = models.DateField(null=True, blank=True)
    rental_status = models.CharField(max_length=20, choices=[
        ('rented', 'Rented'),
        ('returned', 'Returned'),
    ], default='rented')
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True, default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.rental_end_date:
            self.rental_end_date = self.rental_start_date + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} rented by {self.user.username}"

    def is_returned(self):
        return self.rental_status == 'returned'


class RentalList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rental = models.ForeignKey('Rental', on_delete=models.CASCADE)  # Linking to existing Rental model
    rental_start_date = models.DateField(auto_now_add=True)
    rental_end_date = models.DateField(null=True, blank=True)
    rental_status = models.CharField(max_length=20, choices=[
        ('rented', 'Rented'),
        ('returned', 'Returned'),
    ], default='rented')
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.rental.book.title} rented by {self.user.username}"
