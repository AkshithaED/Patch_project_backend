from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import timedelta

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
    groups = models.ManyToManyField('auth.Group', related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='customuser_set', blank=True)

    def __str__(self):
        return self.username or 'No username set'

# -----------------------
# SoftDeleteManager
# -----------------------
# class SoftDeleteManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(is_deleted=False)


# -----------------------
# Release Model
# -----------------------
class Release(models.Model):
    name = models.CharField(max_length=255, primary_key=True, default=defaults['release']['name'])
    release_date = models.DateField(default=defaults['release']['release_date'])
    # release_version = models.CharField(max_length=50, default=defaults['release']['release_version'])
    active = models.BooleanField(default=defaults['release']['active'])
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    # objects = SoftDeleteManager()
    def soft_delete(self):
        self.is_deleted = True
        self.save()
        
    def delete(self, using=None, keep_parents=False):
        self.soft_delete()

    def __str__(self):
        return self.name



# -----------------------
# Jar Model
# -----------------------
class Jar(models.Model):
    name = models.CharField(primary_key = True,max_length=255)

    def __str__(self):
        return self.name


# -----------------------
# HighLevelScope Model
# -----------------------
class HighLevelScope(models.Model):
    name = models.CharField(primary_key=True, max_length=255)

    def __str__(self):
        return self.name



# -----------------------
# SecurityIssue Model
# -----------------------

class SecurityIssue(models.Model):
    cve_id = models.CharField(max_length=255, default=defaults['security_issue']['cve_id'])
    cvss_score = models.FloatField(default=defaults['security_issue']['cvss_score'])
    severity = models.CharField(max_length=50, choices=[('Critical', 'Critical'), ('High', 'High'), ('Medium', 'Medium')], default=defaults['security_issue']['severity'])
    affected_libraries = models.TextField(default=defaults['security_issue']['affected_libraries'])
    library_path = models.CharField(max_length=500, blank=True, default=defaults['security_issue']['library_path'])
    description = models.TextField(default="Security issue description")
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    # objects = SoftDeleteManager()
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cve_id', 'cvss_score', 'severity', 'affected_libraries'], name='unique_security_issue')
        ]
    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def delete(self, using=None, keep_parents=False):
        self.soft_delete()
    
    def __str__(self):
        return f"Security Issue {self.cve_id}"

# -----------------------
# Product Model
# -----------------------
class Product(models.Model):
    name = models.CharField(max_length=255, primary_key=True, default=defaults['product']['name'])
    # version = models.CharField(max_length=50, default=defaults['product']['version'])
    status = models.CharField(max_length=50, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default=defaults['product']['status'])
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    # objects = SoftDeleteManager()
    
    
    # Add the ManyToManyField with through here
    security_issues = models.ManyToManyField(SecurityIssue, through='ProductSecurityIssue', related_name='products')

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def delete(self, using=None, keep_parents=False):
        self.soft_delete()

    def __str__(self):
        return self.name




# -----------------------
# Image Model
# -----------------------

class Image(models.Model):
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)
    image_name = models.CharField(default=defaults['image']['image_name'], max_length=255)
    build_number = models.CharField(max_length=100, default=defaults['image']['build_number'])
    release_date = models.DateField(default=defaults['release']['release_date'])
    twistlock_report_url = models.URLField(default=defaults['image']['twistlock_report_url'], null=True, blank=True)
    twistlock_report_clean = models.BooleanField(default=True, null=True, blank=True)
    security_issues = models.ManyToManyField(SecurityIssue, related_name='images', blank=True)
    size = models.CharField(max_length=255, null=True, blank=True)
    layers = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    # objects = SoftDeleteManager()

    
    class Meta:
        unique_together = ('image_name', 'build_number')

    def twistlock_status(self):
        if self.twistlock_report_clean:
            return "Clean"
        else:
            return [issue.cve_id for issue in self.security_issues.all()]

    def soft_delete(self):
        self.is_deleted = True
        self.save()
    
    def delete(self, using=None, keep_parents=False):
        self.soft_delete()

    def __str__(self):
        return f"Image for {self.product.name} - Build {self.build_number}"

# -----------------------
# PatchJar Model
# -----------------------       
class PatchJar(models.Model):

    patch   = models.ForeignKey('Patch', on_delete=models.CASCADE)
    jar     = models.ForeignKey('Jar',   on_delete=models.CASCADE)
    remarks = models.TextField(blank=True)
    version = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated    = models.BooleanField(default=False)
    class Meta:
        unique_together = ('patch', 'jar')


# -----------------------
# PatchProductJar Model
# -----------------------
class PatchProductJar(models.Model):
    # patch = models.ForeignKey('Patch', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    # jar = models.ForeignKey('Jar', on_delete=models.CASCADE)
    patch_jar_id = models.ForeignKey('PatchJar', on_delete=models.CASCADE)
    current_version = models.CharField(max_length=100, blank=True, null=True)  # Existing version
    # version = models.CharField(max_length=100, blank=True, null=True) 
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.BooleanField(default=False)

    class Meta:
        unique_together = ('patch_jar_id', 'product')
        verbose_name = 'Patch Product Jar'
        verbose_name_plural = 'Patch Product Jars'

    def __str__(self):
        return f"{self.patch.name} - {self.product.name} - {self.jar.name}"

# -----------------------
# PatchImageJar Model
# -----------------------
class PatchImageJar(models.Model):
    patch_image = models.ForeignKey('PatchImage', on_delete=models.CASCADE)
    jar = models.ForeignKey('Jar', on_delete=models.CASCADE)
    current_version = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.BooleanField(default=False)

    class Meta:
        unique_together = ('patch_image', 'jar')
        verbose_name = 'Patch Image Jar'
        verbose_name_plural = 'Patch Image Jars'

    def __str__(self):
        return f"{self.patch_image.patch.name} - Image #{self.patch_image.id} - {self.jar.name}"
    
# -----------------------
# PatchHighLevelScope Model
# -----------------------  
class PatchHighLevelScope(models.Model):
    patch   = models.ForeignKey('Patch', on_delete=models.CASCADE)
    scope   = models.ForeignKey('HighLevelScope', on_delete=models.CASCADE)
    version = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patch', 'scope')



# -----------------------
# Patch Model
# -----------------------
class Patch(models.Model):
    PATCH_STATE_CHOICES = [
        ('new', 'New'),
        ('cancelled', 'Cancelled'),
        ('released', 'Released'),
        ('in_progress', "In progress")
    ]
    
    name = models.CharField(max_length=255, primary_key=True)
    release = models.ForeignKey(Release, on_delete=models.CASCADE, related_name='patches')
    release_date = models.DateField()
    kick_off = models.DateField()
    code_freeze = models.DateField()
    platform_qa_build = models.DateField()
    client_build_availability = models.DateField()
    description = models.TextField()
    # patch_version = models.CharField(max_length=50)

    kba = models.CharField(max_length=500, blank=True)
    functional_fixes = models.CharField(max_length=500, blank=True)
    security_issues = models.CharField(max_length=500, blank=True)


    patch_state = models.CharField(max_length=20, choices=PATCH_STATE_CHOICES, default='new')
    
    products = models.ManyToManyField(
        Product, 
        related_name='patches'
    )
    images = models.ManyToManyField(
        Image, 
         through='PatchProductImage', 
        related_name='patches'
    )
    # third_party_jars = models.ManyToManyField(Jar, related_name='patches', blank=True)
    # high_level_scope = models.ManyToManyField(HighLevelScope, related_name='patches', blank=True)
    third_party_jars = models.ManyToManyField(
       Jar,
       through='PatchJar',
       related_name='patch_links'
    )
    high_level_scope = models.ManyToManyField(
       HighLevelScope,
       through='PatchHighLevelScope',
       related_name='patch_links'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    # objects = SoftDeleteManager()


    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def delete(self, using=None, keep_parents=False):
        self.soft_delete()

    def __str__(self):
        return self.name


# -----------------------
# PatchProductImage Model
# ------------------------
class PatchProductImage(models.Model):
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            # Ensure the same image is not added to the same patch twice.
            models.UniqueConstraint(
                fields=['patch', 'image'], 
                name='unique_patch_image'
            ),
        ]
    def clean(self):
        # Ensure the image belongs to the selected product
        if self.image.product != self.product:
            raise ValidationError("Image must belong to the selected product.")



# -----------------------
# Patchimage Model
# -----------------------
STATUS_CHOICES = [
    ('Released', 'Released'),
    ('Not Released', 'Not Released'),
    ('Applicable', 'Applicable'),
]

class PatchImage(models.Model):
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    
    ot2_pass = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='Not Released',
        blank=True,
        null=True,
    )
    registry = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='Not Released',
        blank=True,
        null=True,
    )
    patch_build_number = models.CharField(max_length=50, blank=True, null=True)

    # other patch-specific fields related to this image

class PatchProductHelmChart(models.Model):
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    helm_charts = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='Not Released',
        blank=True,
        null=True,
    )



class ProductSecurityIssue(models.Model):
    # patch = models.ForeignKey('Patch', on_delete=models.CASCADE)  # NEW
    patch = models.ForeignKey(Patch, on_delete=models.CASCADE, null=True, blank=True)

    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    security_issue = models.ForeignKey(SecurityIssue, on_delete=models.CASCADE)
    product_security_des = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('patch', 'product', 'security_issue')  # UPDATED

# -----------------------
# ProductJarRelease Model
# -----------------------
class ProductJarRelease(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    jar = models.CharField(max_length=255)
    release = models.ForeignKey(Release, on_delete=models.CASCADE)
    path = models.CharField(max_length=500)

    class Meta:
        unique_together = ('product', 'jar', 'release')

    def __str__(self):
        return f"{self.product.name} - {self.jar.name} - {self.release.name}"

# -----------------------
# ProductImageRelease Model
# -----------------------

class ReleaseProductImage(models.Model):
    release = models.ForeignKey('Release', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)       
    image_name = models.CharField(max_length=255)      

    # Registry source
    registry_registry = models.URLField()
    registry_path = models.CharField(max_length=255, blank=True)
    registry_image_name = models.CharField(max_length=255)

    # ot2paas source
    ot2paas_registry = models.URLField()
    ot2paas_path = models.CharField(max_length=255, blank=True)
    ot2paas_image_name = models.CharField(max_length=255)

    # Local source
    local_registry = models.URLField()
    local_path = models.CharField(max_length=255, blank=True)
    local_image_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('release', 'product', 'image_name')

    def __str__(self):
        return f"{self.release} - {self.product} - {self.image_name}"
