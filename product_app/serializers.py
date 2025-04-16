from rest_framework import serializers
from .models import Release, Patch, Product, Image, SecurityIssue


class SecurityIssueSerializer(serializers.ModelSerializer):
    image = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.filter(twistlock_report_clean=False, is_deleted=False)
    )

    class Meta:
        model = SecurityIssue
        fields = '__all__'



class ImageSerializer(serializers.ModelSerializer):
    security_issues = SecurityIssueSerializer(many=True, read_only=True)
    ot2_pass = serializers.ChoiceField(choices=[('Yes', 'Yes'), ('No', 'No')])  # Serialize ot2_pass to 'Yes'/'No'

    class Meta:
        model = Image
        fields = ['image_url', 'build_number', 'release_date', 'ot2_pass', 'twistlock_report_url', 
                  'twistlock_report_clean', 'is_deleted', 'product', 'timestamp', 'security_issues']

    def get_ot2_pass(self, obj):
        # This method returns 'Yes' if True, 'No' if False
        return "Yes" if obj.ot2_pass else "No"

    def validate_ot2_pass(self, value):
        # Converts 'Yes'/'No' into True/False
        if value == 'Yes':
            return True
        elif value == 'No':
            return False
        return value

class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    related_patches = serializers.SerializerMethodField()
    patches = serializers.PrimaryKeyRelatedField(queryset=Patch.objects.all(), many=True, write_only=True)

    class Meta:
        model = Product
        fields = ['name', 'version', 'status', 'is_deleted', 'timestamp', 'images', 'related_patches', 'patches']

    def get_related_patches(self, obj):
        # Get patches related to this product and return their names only
        patches = obj.patches_set.filter(is_deleted=False)
        return [patch.name for patch in patches]

    def create(self, validated_data):
        patches = validated_data.pop('patches', [])
        product = Product.objects.create(**validated_data)
        product.patches.set(patches)  # Use patches_set to link patches to product
        return product

    def update(self, instance, validated_data):
        patches = validated_data.pop('patches', [])
        instance = super().update(instance, validated_data)
        instance.patches.set(patches)  # Update patches using patches_set
        return instance

class PatchSerializer(serializers.ModelSerializer):
    related_products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Patch
        fields = '__all__'

class ReleaseSerializer(serializers.ModelSerializer):
    patches = PatchSerializer(many=True, read_only=True)

    class Meta:
        model = Release
        fields = '__all__'
