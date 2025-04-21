from rest_framework import serializers
from .models import Release, Patch, Product, Image, SecurityIssue


class SecurityIssueSerializer(serializers.ModelSerializer):
    image = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.filter(twistlock_report_clean=False, is_deleted=False)
    )

    class Meta:
        model = SecurityIssue
        fields = [
            'image', 'cve_id', 'cvss_score', 'severity', 'affected_libraries',
            'library_path', 'description', 'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ImageSerializer(serializers.ModelSerializer):
    security_issues = SecurityIssueSerializer(many=True, read_only=True)
    ot2_pass = serializers.ChoiceField(choices=[('Yes', 'Yes'), ('No', 'No')])

    class Meta:
        model = Image
        fields = [
            'image_url', 'build_number', 'release_date', 'ot2_pass',
            'twistlock_report_url', 'twistlock_report_clean', 'is_deleted',
            'product', 'created_at', 'updated_at', 'security_issues'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_ot2_pass(self, value):
        if value not in ['Yes', 'No']:
            raise serializers.ValidationError("ot2_pass must be 'Yes' or 'No'")
        return value


# Simplified image list
class ImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['twistlock_report_clean']


# Patch name only for ReleaseList
class PatchNameOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Patch
        fields = ['name']


# Product name only for PatchList
class ProductNameOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name']


# Release: Full Detail
class ReleaseSerializer(serializers.ModelSerializer):
    patches = PatchNameOnlySerializer(many=True, read_only=True)

    class Meta:
        model = Release
        fields = [
            'name', 'release_date', 'active', 'release_version',
            'is_deleted', 'created_at', 'updated_at', 'patches'
        ]
        read_only_fields = ['created_at', 'updated_at']


# Release: List view
class ReleaseListSerializer(serializers.ModelSerializer):
    patches = serializers.SerializerMethodField()

    class Meta:
        model = Release
        fields = ['name', 'release_date', 'active', 'release_version', 'patches']

    def get_patches(self, obj):
        return [patch.name for patch in obj.patches.filter(is_deleted=False)]


# Patch: Full Detail
class PatchSerializer(serializers.ModelSerializer):
    related_products = ProductNameOnlySerializer(many=True, read_only=True)

    class Meta:
        model = Patch
        fields = [
            'name', 'release', 'description', 'patch_version',
            'patch_state', 'related_products', 'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# Patch: List view
class PatchListSerializer(serializers.ModelSerializer):
    related_products = serializers.SerializerMethodField()

    class Meta:
        model = Patch
        fields = ['name', 'patch_version', 'patch_state', 'related_products']

    def get_related_products(self, obj):
        return [product.name for product in obj.related_products.filter(is_deleted=False)]


# Product: Full Detail
class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    related_patches = serializers.SerializerMethodField()
    patches = serializers.PrimaryKeyRelatedField(queryset=Patch.objects.all(), many=True, write_only=True)

    class Meta:
        model = Product
        fields = [
            'name', 'version', 'status', 'is_deleted', 'created_at',
            'updated_at', 'images', 'related_patches', 'patches'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_related_patches(self, obj):
        return [patch.name for patch in obj.patches_set.filter(is_deleted=False)]

    def create(self, validated_data):
        patches = validated_data.pop('patches', [])
        product = Product.objects.create(**validated_data)
        for patch in patches:
            patch.related_products.add(product)
        return product

    def update(self, instance, validated_data):
        patches = validated_data.pop('patches', [])
        instance = super().update(instance, validated_data)
        instance.patches_set.clear()
        for patch in patches:
            patch.related_products.add(instance)
        return instance


# Product: List view
class ProductListSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'version', 'status', 'is_deleted', 'created_at', 'updated_at', 'images']

    def get_images(self, obj):
        return [img.image_url for img in obj.images.filter(is_deleted=False)]
