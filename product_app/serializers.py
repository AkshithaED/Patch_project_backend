from rest_framework import serializers
from .models import (
    HighLevelScope, Release, Patch, Product, Image,
    SecurityIssue, ThirdPartyJar
)


# ---------------------------
# SecurityIssue Serializers
# ---------------------------
class SecurityIssueSerializer(serializers.ModelSerializer):
    image = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.filter(twistlock_report_clean=False, is_deleted=False)
    )

    class Meta:
        model = SecurityIssue
        fields = [
            'image', 'cve_id', 'cvss_score', 'severity', 'affected_libraries',
            'library_path', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


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


# ---------------------------
# Release Serializers
# ---------------------------
class PatchNameOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Patch
        fields = ['name']


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


# ---------------------------
# ThirdPartyJar Serializer
# ---------------------------
class ThirdPartyJarSerializer(serializers.ModelSerializer):
    jar_name_display = serializers.CharField(source='get_jar_name_display', read_only=True)

    class Meta:
        model = ThirdPartyJar
        fields = ['jar_name', 'jar_name_display', 'version']


# ---------------------------
# Patch Serializers
# ---------------------------
class ProductImageMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image_name', 'build_number', 'twistlock_report_clean', 'release_date']


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
    high_level_scopes = serializers.SlugRelatedField(
        slug_field='name',
        queryset=HighLevelScope.objects.all(),
        many=True
    )
    third_party_jars = ThirdPartyJarSerializer(many=True)

    class Meta:
        model = Patch
        fields = [
            'name', 'release', 'release_date', 'kick_off', 'code_freeze',
            'platform_qa_build', 'client_build_availability', 'description',
            'patch_version', 'patch_state', 'related_products',
            'product_images', 'high_level_scopes', 'third_party_jars',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        products = instance.related_products.filter(is_deleted=False)
        nested_products = []

        for product in products:
            images = instance.product_images.filter(product=product, is_deleted=False)
            nested_products.append({
                "name": product.name,
                "product_images": ProductImageMiniSerializer(images, many=True).data
            })

        rep['related_products'] = nested_products
        rep.pop('product_images', None)
        return rep

    def create(self, validated_data):
        prods = validated_data.pop('related_products', [])
        imgs = validated_data.pop('product_images', [])
        high_level_scopes = validated_data.pop('high_level_scopes', [])
        third_party_jars = validated_data.pop('third_party_jars', [])

        patch = Patch.objects.create(**validated_data)
        patch.related_products.set(prods)
        patch.product_images.set(imgs)
        patch.high_level_scopes.set(high_level_scopes)

        for jar_data in third_party_jars:
            ThirdPartyJar.objects.create(patch=patch, **jar_data)

        return patch

    def update(self, instance, validated_data):
        prods = validated_data.pop('related_products', [])
        imgs = validated_data.pop('product_images', [])
        high_level_scopes = validated_data.pop('high_level_scopes', [])
        third_party_jars = validated_data.pop('third_party_jars', [])

        instance = super().update(instance, validated_data)
        instance.related_products.set(prods)
        instance.product_images.set(imgs)
        instance.high_level_scopes.set(high_level_scopes)

        instance.third_party_jars.all().delete()
        for jar_data in third_party_jars:
            ThirdPartyJar.objects.create(patch=instance, **jar_data)

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
        return [patch.name for patch in obj.patches_set.filter(is_deleted=False)]


class ProductListSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'version', 'status', 'created_at', 'updated_at', 'images']

    def get_images(self, obj):
        return [img.image_url for img in obj.images.filter(is_deleted=False)]
