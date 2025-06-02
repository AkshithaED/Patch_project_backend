from rest_framework.response import Response
from django.db import transaction
from rest_framework import viewsets, status, serializers
from .models import Release, Patch, Product, Image, Jar, HighLevelScope, SecurityIssue, PatchProductImage
from .serializers import ReleaseSerializer, PatchSerializer, ProductSerializer, ImageSerializer, SecurityIssueSerializer, JarSerializer, HighLevelScopeSerializer
from rest_framework.decorators import api_view


class ReleaseViewSet(viewsets.ModelViewSet):
    queryset = Release.objects.filter(is_deleted=False)
    serializer_class = ReleaseSerializer
    lookup_field = 'name' 

class PatchViewSet(viewsets.ModelViewSet):
    queryset         = Patch.objects.filter(is_deleted=False)
    serializer_class = PatchSerializer
    lookup_field     = 'name'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    lookup_field = 'name'

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.filter(is_deleted=False)
    serializer_class = ImageSerializer
    lookup_field = 'image_name'

class SecurityIssueViewSet(viewsets.ModelViewSet):
    queryset = SecurityIssue.objects.filter(is_deleted=False)
    serializer_class = SecurityIssueSerializer
    lookup_field = 'cve_id'

class JarViewSet(viewsets.ModelViewSet):
    queryset = Jar.objects.all()
    serializer_class = JarSerializer
    lookup_field = 'name'

class HighLevelScopeViewSet(viewsets.ModelViewSet):
    queryset = HighLevelScope.objects.all()
    serializer_class = HighLevelScopeSerializer
    lookup_field = 'name'

@api_view(['GET'])
def patch_completion_percentage(request, name):
    try:
        # patch = Patch.objects.get(name=name)
        patch = Patch.objects.get(name=name, is_deleted=False)
    except Patch.DoesNotExist:
        return Response({"error": "Patch not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = PatchSerializer(patch)
    patch_data = serializer.data

    total_items = 0
    completed_items = 0

    #  Check JARs
    for jar in patch_data.get('jars', []):
        total_items += 1
        if jar.get('updated') is True:
            completed_items += 1
        elif jar.get('remarks'):  # updated == False but has remarks
            completed_items += 1

    #  Check product images
    for product in patch_data.get('products', []):
        for image in product.get('images', []):
            total_items += 1  # 1/2 for registry release, 1/2 for OT2_PaaS
            if image.get('registry') and image.get('registry').lower() == 'released':
                completed_items += 0.5
            if image.get('ot2_pass') and image.get('ot2_pass').lower() == 'released':
                completed_items += 0.5

    #  Avoid division by zero
    if total_items == 0:
        return Response({"completion_percentage": 0}, status=status.HTTP_200_OK)

    percentage = round((completed_items / total_items) * 100, 2)
    return Response({"completion_percentage": percentage}, status=status.HTTP_200_OK)