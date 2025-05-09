from rest_framework import serializers
from .models import (
    Release, Patch, Product, Image, SecurityIssue,ThirdPartyJar, HighLevelScope
)
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



# ---------------------------
# Patch Serializers
# ---------------------------
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

    # Using PrimaryKeyRelatedField for ManyToMany relations
    high_level_scope = serializers.PrimaryKeyRelatedField(
        queryset=HighLevelScope.objects.all(),
        many=True
    )

    third_party_jars = serializers.PrimaryKeyRelatedField(
        queryset=ThirdPartyJar.objects.all(),
        many=True
    )

    class Meta:
        model = Patch
        fields = [
            'name', 'release', 'release_date', 'kick_off', 'code_freeze',
            'platform_qa_build', 'client_build_availability', 'description',
            'patch_version', 'patch_state', 'related_products',
            'product_images', 'high_level_scope', 'third_party_jars',
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
        related_products = validated_data.pop('related_products', [])
        product_images = validated_data.pop('product_images', [])
        high_level_scope = validated_data.pop('high_level_scope', [])
        third_party_jars = validated_data.pop('third_party_jars', [])

        patch = Patch.objects.create(**validated_data)
        patch.related_products.set(related_products)
        patch.product_images.set(product_images)
        patch.high_level_scope.set(high_level_scope)  # Ensure it's set correctly
        patch.third_party_jars.set(third_party_jars)  # Ensure it's set correctly

        return patch

    def update(self, instance, validated_data):
        related_products = validated_data.pop('related_products', [])
        product_images = validated_data.pop('product_images', [])
        high_level_scope = validated_data.pop('high_level_scope', [])
        third_party_jars = validated_data.pop('third_party_jars', [])

        instance = super().update(instance, validated_data)
        instance.related_products.set(related_products)
        instance.product_images.set(product_images)
        instance.high_level_scope.set(high_level_scope)  # Ensure it's updated
        instance.third_party_jars.set(third_party_jars)  # Ensure it's updated

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
