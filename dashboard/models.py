# dashboard/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('FACILITIES', 'Facilities'),
        ('FINANCE', 'Finance'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='FACILITIES')
    company_name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.email} ({self.role})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class Site(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=200)
    postcode = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    industry_type = models.CharField(max_length=100, blank=True)
    budget_monthly = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.name} ({self.postcode})"


class CostCategory(models.Model):
    """Standard cost categories for consistent breakdowns."""
    name = models.CharField(max_length=100, unique=True)
    is_controllable = models.BooleanField(
        default=False,
        help_text="True for unit rate / demand that can be influenced"
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = "Cost categories"

    def __str__(self):
        return self.name


class Bill(models.Model):
    STATUS_CHOICES = [
        ('UPLOADED', 'Uploaded'),
        ('PARSING', 'Parsing'),
        ('NEEDS_REVIEW', 'Needs Review'),
        ('VALIDATED', 'Validated'),
        ('REJECTED', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='bills')
    period_start = models.DateField()
    period_end = models.DateField()
    supplier = models.CharField(max_length=150, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    file = models.FileField(upload_to='bills/%Y/%m/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPLOADED')
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='uploaded_bills'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period_end']
        indexes = [
            models.Index(fields=['site', 'period_end']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.site.name} | {self.period_start} → {self.period_end} | £{self.total_amount}"


class BillLineItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='line_items')
    category = models.ForeignKey(
        CostCategory, on_delete=models.PROTECT, related_name='line_items'
    )
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(
        max_digits=14, decimal_places=4, null=True, blank=True
    )
    unit = models.CharField(max_length=30, blank=True)  # kWh, days, kVA, etc.
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=6, null=True, blank=True
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    is_validated = models.BooleanField(default=False)

    class Meta:
        ordering = ['category__display_order', 'id']

    def __str__(self):
        return f"{self.category.name}: £{self.amount}"


class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
    ]
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='WARNING')
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity}] {self.title}"


class ActionPlanItem(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
        ('CANCELLED', 'Cancelled'),
    ]
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='action_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    estimated_annual_saving = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='action_items'
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status', '-estimated_annual_saving']

    def __str__(self):
        return self.title
