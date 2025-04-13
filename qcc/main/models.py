from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    street_name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    preferred_contact = models.CharField(
        max_length=10,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('whatsapp', 'WhatsApp')
        ],
        default='email'
    )

    def __str__(self):
        return self.user.username

class Campaign(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    featured_image = models.ImageField(upload_to='campaigns/')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    @property
    def progress_percentage(self):
        if self.goal_amount == 0:
            return 0
        return (self.current_amount / self.goal_amount) * 100

    @property
    def days_left(self):
        return (self.end_date - timezone.now()).days

class CampaignImage(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='campaigns/')

class Donation(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donation_date = models.DateTimeField(default=timezone.now)
    anonymous = models.BooleanField(default=False)
    message = models.TextField(blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='completed'
    )
    transaction_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Donation #{self.id} - {self.amount}"

class Accomplishment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    image = models.ImageField(upload_to='accomplishments/', blank=True, null=True)

    def __str__(self):
        return self.title