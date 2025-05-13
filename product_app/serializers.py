from rest_framework import serializers
from .models import (
    Release, Patch, Product, Image, SecurityIssue,ThirdPartyJar, HighLevelScope
)
from django.core.exceptions import ObjectDoesNotExist

# ---------------------------
# SecurityIssue Serializers
# ---------------------------
class SecurityIssueSerializer(serializers.ModelSerializer):
    image_name = serializers.ChoiceField(
        choices=[],
        write_only=True
    )
    image = serializers.CharField(
        source='image_name.image_name',
        read_only=True
    )

    class Meta:
        model = SecurityIssue
        fields = [
            'image_name',         
            'image',  
            'cve_id',
            'cvss_score',
            'severity',
            'affected_libraries',
            'library_path',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate dropdown with available image names
        self.fields['image_name'].choices = [
            (img.image_name, f"{img.product.name} - Build {img.build_number}")
            for img in Image.objects.filter(is_deleted=False, twistlock_report_clean=False)
        ]

    def create(self, validated_data):
        image_name_str = validated_data.pop('image_name')
        try:
            image = Image.objects.get(image_name=image_name_str, is_deleted=False, twistlock_report_clean=False)
        except Image.DoesNotExist:
            raise serializers.ValidationError({'image_name': 'Invalid or unavailable image name.'})
        return SecurityIssue.objects.create(image_name=image, **validated_data)

class SecurityIssueNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityIssue
        fields = [
            'cve_id', 'cvss_score', 'severity', 'affected_libraries',
            'library_path', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# ---------------------------
# Image Serializers
# ---------------------------
class ImageSerializer(serializers.ModelSerializer):
    security_issues = serializers.SerializerMethodField()
    ot2_pass = serializers.ChoiceField(choices=[('Yes', 'Yes'), ('No', 'No')])

    class Meta:
        model = Image
        fields = [
            'image_name', 'build_number', 'release_date', 'ot2_pass',
            'twistlock_report_url', 'twistlock_report_clean',
            'product', 'created_at', 'updated_at', 'security_issues'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_security_issues(self, obj):
        issues = obj.security_issues_set.filter(is_deleted=False)
        return SecurityIssueNestedSerializer(issues, many=True).data


class ImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['twistlock_report_clean']


class PatchNameOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Patch
        fields = ['name']

# ---------------------------
# Release Serializers
# ---------------------------
class ReleaseSerializer(serializers.ModelSerializer):
    patches = PatchNameOnlySerializer(many=True, read_only=True)

    class Meta:
        model = Release
        fields = [
            'name', 'release_date', 'active', 'release_version',
            'created_at', 'updated_at', 'patches'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ReleaseListSerializer(serializers.ModelSerializer):
    patches = serializers.SerializerMethodField()

    class Meta:
        model = Release
        fields = ['name', 'release_date', 'active', 'release_version', 'patches']

    def get_patches(self, obj):
        return [patch.name for patch in obj.patches.filter(is_deleted=False)]


class ProductImageMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image_name']



from rest_framework import serializers
from .models import (
    Release, Patch, Product, Image, SecurityIssue, ThirdPartyJar, HighLevelScope,
    PatchThirdPartyJar, PatchHighLevelScope
)
# Third Party Jar Serializer
class ThirdPartyJarSerializer(serializers.ModelSerializer):
    version = serializers.CharField()
    remarks = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = ThirdPartyJar
        fields = ['name', 'version', 'remarks']


# High Level Scope Serializer
class HighLevelScopeSerializer(serializers.ModelSerializer):
    version = serializers.CharField()

    class Meta:
        model = HighLevelScope
        fields = ['name', 'version']

# serializers.py

class PatchHighLevelScopeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='scope.name')

    class Meta:
        model = PatchHighLevelScope
        fields = ['name', 'version']


class PatchThirdPartyJarSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='jar.name')
    remarks = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = PatchThirdPartyJar
        fields = ['name', 'version', 'remarks']
  

# Patch Serializer
class PatchSerializer(serializers.ModelSerializer):
    related_products = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Product.objects.filter(is_deleted=False),
        many=True
    )
    product_images = serializers.SlugRelatedField(
        slug_field='image_name',
        queryset=Image.objects.filter(is_deleted=False),
        many=True
    )
    
    # These are used for reading
    high_level_scope = serializers.SerializerMethodField()
    third_party_jars = serializers.SerializerMethodField()

    # These are used for writing
    high_level_scope_input = HighLevelScopeSerializer(many=True, write_only=True)
    third_party_jars_input = ThirdPartyJarSerializer(many=True, write_only=True)

    class Meta:
        model = Patch
        fields = [
            'name', 'release', 'release_date', 'kick_off', 'code_freeze',
            'platform_qa_build', 'client_build_availability', 'description',
            'patch_version', 'patch_state', 'related_products',
            'product_images',
            'high_level_scope',         # For GET
            'high_level_scope_input',   # For POST/PUT
            'third_party_jars',         # For GET
            'third_party_jars_input',   # For POST/PUT
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_high_level_scope(self, obj):
        items = PatchHighLevelScope.objects.filter(patch=obj)
        return PatchHighLevelScopeSerializer(items, many=True).data

    def get_third_party_jars(self, obj):
        items = PatchThirdPartyJar.objects.filter(patch=obj)
        return PatchThirdPartyJarSerializer(items, many=True).data

    def create(self, validated_data):
        related_products = validated_data.pop('related_products', [])
        product_images = validated_data.pop('product_images', [])
        high_level_scope_data = validated_data.pop('high_level_scope_input', [])
        third_party_jars_data = validated_data.pop('third_party_jars_input', [])

        patch = Patch.objects.create(**validated_data)
        patch.related_products.set(related_products)
        patch.product_images.set(product_images)

        for scope_data in high_level_scope_data:
            try:
                scope = HighLevelScope.objects.get(name=scope_data['name'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"HighLevelScope '{scope_data['name']}' does not exist.")
            PatchHighLevelScope.objects.create(patch=patch, scope=scope, version=scope_data['version'])

        for jar_data in third_party_jars_data:
            try:
                jar = ThirdPartyJar.objects.get(name=jar_data['name'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"ThirdPartyJar '{jar_data['name']}' does not exist.")
            PatchThirdPartyJar.objects.create(
                patch=patch, jar=jar,
                version=jar_data['version'],
                remarks=jar_data.get('remarks', '')
            )

        return patch

    def update(self, instance, validated_data):
        related_products = validated_data.pop('related_products', [])
        product_images = validated_data.pop('product_images', [])
        high_level_scope_data = validated_data.pop('high_level_scope_input', [])
        third_party_jars_data = validated_data.pop('third_party_jars_input', [])

        instance = super().update(instance, validated_data)
        instance.related_products.set(related_products)
        instance.product_images.set(product_images)

        # Clear and reassign many-to-many through models
        PatchHighLevelScope.objects.filter(patch=instance).delete()
        PatchThirdPartyJar.objects.filter(patch=instance).delete()

        for scope_data in high_level_scope_data:
            scope = HighLevelScope.objects.get(name=scope_data['name'])
            PatchHighLevelScope.objects.create(patch=instance, scope=scope, version=scope_data['version'])

        for jar_data in third_party_jars_data:
            jar = ThirdPartyJar.objects.get(name=jar_data['name'])
            PatchThirdPartyJar.objects.create(
                patch=instance, jar=jar,
                version=jar_data['version'],
                remarks=jar_data.get('remarks', '')
            )

        return instance


class PatchListSerializer(serializers.ModelSerializer):
    related_products = serializers.SerializerMethodField()

    class Meta:
        model = Patch
        fields = ['name', 'patch_version', 'patch_state', 'related_products']

    def get_related_products(self, obj):
        return [product.name for product in obj.related_products.filter(is_deleted=False)]

# ---------------------------
# Product Serializers
# ---------------------------
class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    patches = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'name', 'version', 'status',
            'created_at', 'updated_at', 'images', 'patches'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_patches(self, obj):
     return [patch.name for patch in obj.patches.filter(is_deleted=False)]



class ProductListSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'version', 'status', 'created_at', 'updated_at', 'images']

    def get_images(self, obj):
        return [img.image_url for img in obj.images.filter(is_deleted=False)]
