from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Release, Patch, Product, Image, SecurityIssue, CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm, PatchAdminForm

# -----------------------
# Custom User Admin
# -----------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ("email", "role", "is_staff", "has_usable_password")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email",)

    def has_usable_password(self, obj):
        return obj.has_usable_password()
    has_usable_password.boolean = True  # Adds ✅/❌ icon in admin

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Personal info", {"fields": ("role",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "password1", "password2", "is_staff", "is_active")
        }),
    )

# -----------------------
# Model Registrations
# -----------------------

@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'release_date', 'active')

@admin.register(Patch)
class PatchAdmin(admin.ModelAdmin):
    form = PatchAdminForm
    list_display = ('name', 'release', 'patch_version')
    filter_horizontal = ('high_level_scope', 'third_party_jars')

    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'status')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('build_number', 'product', 'twistlock_report_clean')

@admin.register(SecurityIssue)
class SecurityIssueAdmin(admin.ModelAdmin):
    list_display = ('cve_id', 'cvss_score', 'severity', 'image')
