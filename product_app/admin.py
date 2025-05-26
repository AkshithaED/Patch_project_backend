from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    CustomUser, Release, Patch, Product,
    Image, SecurityIssue, Jar, HighLevelScope,
    PatchProductImage
)
from .forms import CustomUserCreationForm, CustomUserChangeForm, PatchAdminForm

# -----------------------
# Inline Admin Classes
# -----------------------

class SecurityIssueImageInline(admin.TabularInline):
    model = Image.security_issues.through
    extra = 1
    raw_id_fields = ('image',)

class PatchThirdPartyJarInline(admin.TabularInline):
    model = Patch.third_party_jars.through
    extra = 1

class PatchHighLevelScopeInline(admin.TabularInline):
    model = Patch.high_level_scope.through
    extra = 1

# -----------------------
# Custom User Admin
# -----------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("username", "email", "role", "is_active", "has_usable_password")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")
    ordering = ("-date_joined",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("email", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "password1", "password2", "is_staff", "is_active")
        }),
    )

    def has_usable_password(self, obj):
        return obj.has_usable_password()
    has_usable_password.boolean = True
    has_usable_password.short_description = "Has Password"

# -----------------------
# Release Admin
# -----------------------
@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'release_date', 'active', 'created_at')
    list_filter = ('active', 'release_date')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    

# -----------------------
# Patch Admin
# -----------------------
@admin.register(Patch)
class PatchAdmin(admin.ModelAdmin):
    form = PatchAdminForm
    list_display = ('name', 'release', 'patch_state', 'kick_off', 'code_freeze')
    list_filter = ('patch_state', 'release__name')
    search_fields = ('name', 'release__name')
    raw_id_fields = ('release',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [
        PatchThirdPartyJarInline,
        PatchHighLevelScopeInline
    ]


# -----------------------
# Product Admin
# -----------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'latest_image', 'active_patches_count')
    list_filter = ('status',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    def latest_image(self, obj):
        image = obj.images.filter(is_deleted=False).order_by('-created_at').first()
        return image.image_name if image else "-"
    latest_image.short_description = "Latest Image"

    def active_patches_count(self, obj):
        return obj.patches.filter(is_deleted=False).count()
    active_patches_count.short_description = "Active Patches"

# -----------------------
# Image Admin
# -----------------------
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('image_name', 'product', 'build_number', 'twistlock_status', 'security_issues_list')
    list_filter = ('product__name', 'twistlock_report_clean')
    search_fields = ('image_name', 'product__name')
    raw_id_fields = ('product',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SecurityIssueImageInline]

    def twistlock_status(self, obj):
        color = 'green' if obj.twistlock_report_clean else 'red'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            "Clean" if obj.twistlock_report_clean else "Vulnerable"
        )
    twistlock_status.short_description = "Twistlock Status"

    def security_issues_list(self, obj):
        return ", ".join([issue.cve_id for issue in obj.security_issues.all()])
    security_issues_list.short_description = "Security Issues"

# -----------------------
# Security Issue Admin
# -----------------------
@admin.register(SecurityIssue)
class SecurityIssueAdmin(admin.ModelAdmin):
    list_display = ('cve_id', 'cvss_score', 'severity', 'affected_images_count')
    list_filter = ('severity',)
    search_fields = ('cve_id', 'affected_libraries')
    readonly_fields = ('created_at', 'updated_at')

    def affected_images_count(self, obj):
        return obj.images.count()
    affected_images_count.short_description = "Affected Images"

# -----------------------
# Supporting Models Admin
# -----------------------
@admin.register(Jar)
class JarAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_version')
    search_fields = ('name',)

@admin.register(HighLevelScope)
class HighLevelScopeAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_version')
    search_fields = ('name',)

@admin.register(PatchProductImage)
class PatchProductImageAdmin(admin.ModelAdmin):
    list_display = ('patch', 'product', 'image')
    list_filter = ('patch__name', 'product__name')
    search_fields = ('patch__name', 'product__name', 'image__image_name')