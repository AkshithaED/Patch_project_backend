from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import HighLevelScope, PatchHighLevelScope, PatchThirdPartyJar, Release, Patch, Product, Image, SecurityIssue, CustomUser, ThirdPartyJar
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

@admin.register(HighLevelScope)
class HighLevelScopeAdmin(admin.ModelAdmin):
    search_fields = ('name',)  # Enable search for the autocomplete
    list_display = ('name', 'get_version')  # Display name and version

    def get_version(self, obj):
        return ', '.join([phs.version for phs in PatchHighLevelScope.objects.filter(scope=obj)])
    get_version.short_description = 'Version'

@admin.register(ThirdPartyJar)
class ThirdPartyJarAdmin(admin.ModelAdmin):
    search_fields = ('name',)  # Enable search for the autocomplete
    list_display = ('name', 'get_version', 'get_remarks')  # Display name, version, and remarks

    def get_version(self, obj):
        return ', '.join([ptj.version for ptj in PatchThirdPartyJar.objects.filter(jar=obj)])
    get_version.short_description = 'Version'

    def get_remarks(self, obj):
        return ', '.join([ptj.remarks for ptj in PatchThirdPartyJar.objects.filter(jar=obj)])
    get_remarks.short_description = 'Remarks'

class PatchThirdPartyJarInline(admin.TabularInline):
    model = PatchThirdPartyJar
    extra = 1

class PatchHighLevelScopeInline(admin.TabularInline):
    model = PatchHighLevelScope
    extra = 1

@admin.register(Patch)
class PatchAdmin(admin.ModelAdmin):
    form = PatchAdminForm
    list_display = ('name', 'release', 'patch_version')
    raw_id_fields = ('release',)
    autocomplete_fields = ('high_level_scope', 'third_party_jars')
    search_fields = ('name', 'patch_version', 'release__name')
    inlines = [PatchThirdPartyJarInline, PatchHighLevelScopeInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'status')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('build_number', 'product', 'twistlock_report_clean')

@admin.register(SecurityIssue)
class SecurityIssueAdmin(admin.ModelAdmin):
    list_display = ('cve_id', 'cvss_score', 'severity', 'image_name')


 
