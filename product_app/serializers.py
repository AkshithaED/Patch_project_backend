
from rest_framework import serializers
from .models import Release, Patch, Product, Image, Jar, HighLevelScope, SecurityIssue

class ReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = '__all__'

class JarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jar
        fields = '__all__'

class HighLevelScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HighLevelScope
        fields = '__all__'

class SecurityIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityIssue
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    security_issues = SecurityIssueSerializer(many=True, read_only=True)
    class Meta:
        model = Image
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

class PatchSerializer(serializers.ModelSerializer):
    third_party_jars = JarSerializer(many=True, read_only=True)
    high_level_scope = HighLevelScopeSerializer(many=True, read_only=True)
    class Meta:
        model = Patch
        exclude = ('products', 'images')  # Don't show directly
        # fields = '__all__'
