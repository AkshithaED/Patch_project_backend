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
# Third Party Jar Model (as a choice list)
# -----------------------
class ThirdPartyJar(models.Model):
    name = models.CharField(max_length=255, choices=[
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
    ])
    
    def __str__(self):
        return self.name

# -----------------------
# High Level Scope Model (as a choice list)
# -----------------------
class HighLevelScope(models.Model):
    name = models.CharField(max_length=255, choices=[
        ('alpine', 'Alpine Linux Base Image'),
        ('base_os', 'Base OS'),
        ('tomcat', 'Tomcat'),
        ('jdk', 'JDK'),
        ('otds', 'OTDS'),
        ('otiv', 'OTIV'),
        ('new_relic', 'New Relic'),
    ])
    
    def __str__(self):
        return self.name

class Patch(models.Model):
    PATCH_STATE_CHOICES = [
        ('new', 'New'),
        ('rejected', 'Rejected'),
        ('released', 'Released'),
        ('verified', 'Verified'),
    ]
    
    name = models.CharField(max_length=255, primary_key=True)
    release = models.ForeignKey(Release, on_delete=models.CASCADE, related_name='patches')
    release_date = models.DateField()
    kick_off = models.DateField()
    code_freeze = models.DateField()
    platform_qa_build = models.DateField()
    client_build_availability = models.DateField()
    description = models.TextField()
    patch_version = models.CharField(max_length=50)
    patch_state = models.CharField(max_length=20, choices=PATCH_STATE_CHOICES, default='new')
    related_products = models.ManyToManyField(Product, related_name='patches')
    product_images = models.ManyToManyField('Image', related_name='patches')
    third_party_jars = models.ManyToManyField(ThirdPartyJar,choices=PATCH_STATE_CHOICES, related_name='patches', blank=True)
    high_level_scope = models.ManyToManyField(HighLevelScope, related_name='patches', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return self.name

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
