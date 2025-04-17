from django.db import models
from django.utils import timezone
from django.conf import settings
from django.conf import settings

defaults = settings.DEFAULTS

# Release model
class Release(models.Model):
    name = models.CharField(max_length=255, primary_key=True, default=defaults['release']['name'])  # PRIMARY KEY
    release_date = models.DateField(default=defaults['release']['release_date'])
    customers = models.CharField(max_length=255, default=defaults['release']['customers'])
    active = models.BooleanField(default=defaults['release']['active'])

    # Timestamp
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()
    
    def __str__(self):
        return self.name


# Product model
class Product(models.Model):
    name = models.CharField(max_length=255, primary_key=True, default=defaults['product']['name'])  # PRIMARY KEY
    version = models.CharField(max_length=50, default=defaults['product']['version'])
    status = models.CharField(max_length=50, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default=defaults['product']['status'])

    # Timestamp
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return self.name


# Patch model
class Patch(models.Model):
    release = models.ForeignKey('Release', related_name="patches", on_delete=models.CASCADE)  # Foreign Key
    name = models.CharField(max_length=255, primary_key=True, default=defaults['patch']['name'])  # Primary Key
    description = models.TextField(default=defaults['patch']['description'])
    patch_version = models.CharField(max_length=50, default=defaults['patch']['patch_version'])

    # Timestamp
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-many relationship with Product
    related_products = models.ManyToManyField(Product, related_name="patches_set")

    # Soft delete
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"Patch {self.name} for {self.release.name}"


# Security Issues Model
class SecurityIssue(models.Model):
    image = models.ForeignKey('Image', related_name='security_issues_set', on_delete=models.CASCADE)  # ForeignKey to Image
    cve_id = models.CharField(max_length=255, default=defaults['security_issue']['cve_id'])
    cvss_score = models.FloatField(default=defaults['security_issue']['cvss_score'])
    severity = models.CharField(max_length=50, choices=[('Critical', 'Critical'), ('High', 'High'), ('Medium', 'Medium')],
                                default=defaults['security_issue']['severity'])
    affected_libraries = models.TextField(default=defaults['security_issue']['affected_libraries'])
    library_path = models.CharField(max_length=500, blank=True, default=defaults['security_issue']['library_path'])
    description = models.TextField(default="Security issue description")

    # Timestamp
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    # Soft delete
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"Security Issue {self.cve_id}"


# Image model
class Image(models.Model):
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)  # Foreign Key
    image_url = models.URLField(default=defaults['image']['image_url'])
    build_number = models.CharField(max_length=100, default=defaults['image']['build_number'])
    release_date = models.DateTimeField(default=defaults['image']['release_date'])

    # Replaced registry with ot2_pass (Yes/No)
    ot2_pass = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')


    twistlock_report_url = models.URLField(default=defaults['image']['twistlock_report_url'])

    # Many-to-many relationship with SecurityIssue
    security_issues = models.ManyToManyField(SecurityIssue, related_name='images', blank=True)

    # Twistlock report clean status (True or False)
    twistlock_report_clean = models.BooleanField(default=True)

    # Timestamp
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False)

    def twistlock_status(self):
        """
        Returns the status of the Twistlock report: 
        - "Clean" if the report is clean.
        - A list of CVE IDs if the report is not clean.
        """
        if self.twistlock_report_clean:
            return "Clean"
        else:
            # Return list of CVE IDs associated with security issues
            related_issues = self.security_issues.all()
            return [issue.cve_id for issue in related_issues]

    def soft_delete(self):
        """Mark the image as deleted."""
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"Image for {self.product.name} - Build {self.build_number}"
