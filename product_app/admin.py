from django.contrib import admin
from .models import Release, Patch, Product, Image, SecurityIssue

@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'release_date', 'customers', 'active')

@admin.register(Patch)
class PatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'release', 'patch_version')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'status')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('build_number', 'product', 'twistlock_report_clean')

@admin.register(SecurityIssue)
class SecurityIssueAdmin(admin.ModelAdmin):
    list_display = ('cve_id', 'cvss_score', 'severity', 'image')
