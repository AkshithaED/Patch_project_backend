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
        # Access from Patch side using related_name 'patches_set'
        patches = obj.patches_set.filter(is_deleted=False)
        return [patch.name for patch in patches]

    def create(self, validated_data):
        patches = validated_data.pop('patches', [])
        product = Product.objects.create(**validated_data)
        for patch in patches:
            patch.related_products.add(product)
        return product

    def update(self, instance, validated_data):
        patches = validated_data.pop('patches', [])
        instance = super().update(instance, validated_data)
        
        # Clear existing and add new
        instance.patches_set.clear()
        for patch in patches:
            patch.related_products.add(instance)
        return instance


class PatchSerializer(serializers.ModelSerializer):
    related_products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Patch
        fields = [
            'name', 'release', 'description', 'patch_version',
            'patch_state',  
            'related_products', 'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']



class ReleaseSerializer(serializers.ModelSerializer):
    patches = PatchSerializer(many=True, read_only=True)

    class Meta:
        model = Release
        fields = [
            'name', 'release_date', 'active',
            'is_deleted', 'created_at', 'updated_at', 'patches'
        ]
        read_only_fields = ['created_at', 'updated_at']
