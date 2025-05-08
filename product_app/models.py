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
# Release Model
# -----------------------
class Release(models.Model):
    name = models.CharField(max_length=255, primary_key=True, default=defaults['release']['name'])
    release_date = models.DateField(default=defaults['release']['release_date'])
    release_version = models.CharField(max_length=50, default=defaults['release']['release_version'])
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
# High Level Scope Model
# -----------------------
class HighLevelScope(models.Model):
    HIGH_LEVEL_CHOICES = [
        ('alpine', 'Alpine Linux Base Image'),
        ('base_os', 'Base OS'),
        ('tomcat', 'Tomcat'),
        ('jdk', 'JDK'),
        ('otds', 'OTDS'),
        ('otiv', 'OTIV'),
        ('new_relic', 'New Relic'),
    ]
    name = models.CharField(
        max_length=100,
        choices=HIGH_LEVEL_CHOICES,
        default='alpine'  
    )
    version = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.get_name_display()} - {self.version}"

# -----------------------
# Third Party Jar Model
# -----------------------
class ThirdPartyJar(models.Model):
    THIRD_PARTY_JARS = [
        ("commons-cli", "commons-cli"),
        ("commons-codec", "commons-codec"),
        ("commons-io", "commons-io"),
        ("log4j", "log4j"),
        ("spring-core", "spring framework (spring-core)"),
        ("spring-security", "spring security"),
        ("xmlsec", "xmlsec"),
        ("logback-core", "logback-core"),
        ("cxf-core", "Cxf-core"),
        ("cxf-bindings-soap", "Cxf-rt-bindings-soap"),
        ("cxf-bindings-xml", "Cxf-rt-bindings-xml"),
        ("cxf-databinding-jaxb", "Cxf-rt-databinding-jaxb"),
        ("cxf-frontend-simple", "Cxf-rt-frontend-simple"),
        ("cxf-frontend-jaxws", "Cxf-rt-frontend-jaxws"),
        ("cxf-transports-http", "Cxf-rt-transports-http"),
        ("cxf-ws-addr", "Cxf-rt-ws-addr"),
        ("cxf-wsdl", "Cxf-rt-wsdl"),
        ("cxf-ws-policy", "Cxf-rt-ws-policy"),
        ("freemarker", "Freemarker Jar"),
        ("netty-all", "netty-all"),
        ("reactor-netty-http", "reactor-netty-http"),
        ("reactor-netty-core", "reactor-netty-core"),
        ("libraries-bom", "libraries-bom"),
        ("httpcore5", "httpcore5"),
        ("guava", "guava"),
        ("jaxb-api", "jaxb-api"),
        ("json", "json"),
        ("logback-classic", "logback-classic"),
        ("jakarta-mail-api", "Jakarta.mail-api"),
        ("spring-boot-parent", "spring-boot-starter-parent"),
    ]
    jar_name = models.CharField(
        max_length=100,
        choices=THIRD_PARTY_JARS,
        default='commons-cli'  # Example key
    )
    version = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.get_jar_name_display()} - {self.version}"


# -----------------------
# Patch Model
# -----------------------
class Patch(models.Model):
    PATCH_STATE_CHOICES = [
        ('new', 'New'),
        ('rejected', 'Rejected'),
        ('released', 'Released'),
        ('verified', 'Verified'),
    ]

    release = models.ForeignKey('Release', related_name="patches", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, primary_key=True, default=defaults['patch']['name'])
    release_date = models.DateField(default=defaults['patch']['release_date'])

    kick_off = models.DateField(blank=True, null=True)
    code_freeze = models.DateField(blank=True, null=True)
    platform_qa_build = models.DateField(blank=True, null=True)
    client_build_availability = models.DateField(blank=True, null=True)

    description = models.TextField(default=defaults['patch']['description'])
    patch_version = models.CharField(max_length=50, default=defaults['patch']['patch_version'])
    patch_state = models.CharField(max_length=20, choices=PATCH_STATE_CHOICES, default='New')
    related_products = models.ManyToManyField('Product', related_name="patches_set")
    product_images = models.ManyToManyField('Image', related_name='patches', blank=True)

    high_level_scopes = models.ManyToManyField('HighLevelScope', through='PatchHighLevelScope', related_name='patches', blank=True)
    third_party_jars = models.ManyToManyField('ThirdPartyJar', through='PatchThirdPartyJar', related_name='patches', blank=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def clean(self):
        if self.release_date and self.release_date <= timezone.now().date():
            raise ValidationError("Release date must be in the future.")

    def save(self, *args, **kwargs):
        if self.release_date:
            self.kick_off = self.kick_off or (self.release_date - timedelta(days=40))
            self.code_freeze = self.code_freeze or (self.release_date - timedelta(days=12))
            self.platform_qa_build = self.platform_qa_build or (self.release_date - timedelta(days=7))
            self.client_build_availability = self.client_build_availability or (self.release_date - timedelta(days=5))
        self.full_clean()
        super().save(*args, **kwargs)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"Patch {self.name} for {self.release.name}"

# ---------------------------------
# Patch to Third Party Jar Model
# ---------------------------------
class PatchThirdPartyJar(models.Model):
    patch = models.ForeignKey('Patch', on_delete=models.CASCADE)
    jar = models.ForeignKey('ThirdPartyJar', on_delete=models.CASCADE)
    version = models.CharField(max_length=50)

    class Meta:
        unique_together = ('patch', 'jar')

    def __str__(self):
        return f"{self.patch.name} - {self.jar.get_jar_name_display()} - v{self.version}"

# ---------------------------------
# Patch to High Level Scope Model
# ---------------------------------
class PatchHighLevelScope(models.Model):
    patch = models.ForeignKey('Patch', on_delete=models.CASCADE)
    scope = models.ForeignKey('HighLevelScope', on_delete=models.CASCADE)
    version = models.CharField(max_length=50)

    class Meta:
        unique_together = ('patch', 'scope')

    def __str__(self):
        return f"{self.patch.name} - {self.scope.get_name_display()} - v{self.version}"

# -----------------------
# Security Issue Model
# -----------------------
class SecurityIssue(models.Model):
    image = models.ForeignKey('Image', related_name='security_issues_set', on_delete=models.CASCADE)
    cve_id = models.CharField(max_length=255, default=defaults['security_issue']['cve_id'])
    cvss_score = models.FloatField(default=defaults['security_issue']['cvss_score'])
    severity = models.CharField(max_length=50, choices=[('Critical', 'Critical'), ('High', 'High'), ('Medium', 'Medium')], default=defaults['security_issue']['severity'])
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


# -----------------------
# Image Model
# -----------------------
class Image(models.Model):
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)
    image_name = models.CharField(default=defaults['image']['image_name'], max_length=255)
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
