from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractUser

defaults = settings.DEFAULTS

# -----------------------
# Custom User Model
# -----------------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('product_manager', 'Product Manager'),
        ('product_owner', 'Product Owner'),
        ('end_user', 'End User'),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='end_user')

    # Fix for reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username or 'No username set'

# -----------------------
# Release Model
# -----------------------
class Release(models.Model):
    name = models.CharField(max_length=255, primary_key=True, default=defaults['release']['name'])
    release_date = models.DateField(default=defaults['release']['release_date'])
    active = models.BooleanField(default=defaults['release']['active'])

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return self.name

# -----------------------
# Product Model
# -----------------------
class Product(models.Model):
    name = models.CharField(max_length=255, primary_key=True, default=defaults['product']['name'])
    version = models.CharField(max_length=50, default=defaults['product']['version'])
    status = models.CharField(max_length=50, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default=defaults['product']['status'])

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return self.name

# -----------------------
# Patch Model
# -----------------------
class Patch(models.Model):
    PATCH_STATE_CHOICES = [
        ('new', 'New'),
        ('rejected', 'Rejected'),
        ('verified', 'Verified'),
    ]

    release = models.ForeignKey('Release', related_name="patches", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, primary_key=True, default=defaults['patch']['name'])
    description = models.TextField(default=defaults['patch']['description'])
    patch_version = models.CharField(max_length=50, default=defaults['patch']['patch_version'])

    patch_state = models.CharField(max_length=20, choices=PATCH_STATE_CHOICES, default='new')  # <-- New field

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    related_products = models.ManyToManyField(Product, related_name="patches_set")

    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"Patch {self.name} for {self.release.name}"

        return f"Patch {self.name} for {self.release.name}"

class SecurityIssue(models.Model):
    image = models.ForeignKey('Image', related_name='security_issues_set', on_delete=models.CASCADE)
    cve_id = models.CharField(max_length=255, default=defaults['security_issue']['cve_id'])
    cvss_score = models.FloatField(default=defaults['security_issue']['cvss_score'])
    severity = models.CharField(max_length=50, choices=[('Critical', 'Critical'), ('High', 'High'), ('Medium', 'Medium')],
                                default=defaults['security_issue']['severity'])
    affected_libraries = models.TextField(default=defaults['security_issue']['affected_libraries'])
    library_path = models.CharField(max_length=500, blank=True, default=defaults['security_issue']['library_path'])
    description = models.TextField(default="Security issue description")

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"Security Issue {self.cve_id}"

class Image(models.Model):
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField(default=defaults['image']['image_url'])
    build_number = models.CharField(max_length=100, default=defaults['image']['build_number'])
    release_date = models.DateTimeField(default=defaults['image']['release_date'])

    ot2_pass = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')
    twistlock_report_url = models.URLField(default=defaults['image']['twistlock_report_url'])

    security_issues = models.ManyToManyField(SecurityIssue, related_name='images', blank=True)
    twistlock_report_clean = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)

    def twistlock_status(self):
        if self.twistlock_report_clean:
            return "Clean"
        else:
            return [issue.cve_id for issue in self.security_issues.all()]

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"Image for {self.product.name} - Build {self.build_number}"
