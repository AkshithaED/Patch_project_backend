from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_list_or_404, get_object_or_404

from .models import Release, Patch, Product, Image, SecurityIssue
from .serializers import (
    ReleaseSerializer, PatchSerializer, ProductSerializer,
    ImageSerializer, SecurityIssueSerializer
)
from .permissions import IsAdmin, IsProductManager, IsProductOwner

class ReleaseViewSet(viewsets.ModelViewSet):
    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer
    permission_classes = [IsAdmin]

class PatchViewSet(viewsets.ModelViewSet):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer
    permission_classes = [IsAdmin | IsProductManager]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdmin | IsProductManager | IsProductOwner]

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAdmin | IsProductOwner]

class SecurityIssueViewSet(viewsets.ModelViewSet):
    queryset = SecurityIssue.objects.all()
    serializer_class = SecurityIssueSerializer
    permission_classes = [IsAdmin | IsProductOwner]

class NestedPatchListView(APIView):
    def get(self, request, release_name):
        release = get_object_or_404(Release, name=release_name)
        patches = release.patches.all()
        serializer = PatchSerializer(patches, many=True)
        return Response(serializer.data)
    
    
class NestedProductListView(APIView):
    def get(self, request, release_name, patch_name):
        # Only get release if it's not soft-deleted (optional if you use soft delete there)
        release = get_object_or_404(Release, name=release_name)

        # Make sure to filter only non-deleted patches
        patch = get_object_or_404(Patch, name=patch_name, release=release, is_deleted=False)

        # Now get related products
        products = patch.related_products.all()
        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data)

class NestedImageListView(APIView):
    def get(self, request, release_name, patch_name, product_name):
        release = get_object_or_404(Release, name=release_name)
        patch = get_object_or_404(Patch, name=patch_name, release=release)
        product = get_object_or_404(Product, name=product_name)
        images = product.images.all()
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data)

class SecurityIssueByImageView(APIView):
    def get(self, request, release_name, patch_name, product_name, build_number):
        product = get_object_or_404(Product, name=product_name)
        image = get_list_or_404(Image, product__name=product_name, build_number=build_number)
        
        # Only show images with twistlock_report_clean=False in the dropdown
        if image.twistlock_report_clean:
            return Response({'status': 'Clean'}, status=200)
        
        issues = image.security_issues.all()
        serializer = ImageSerializer(image, many=True)
        return Response(serializer.data)
    
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Image
from .serializers import ImageSerializer

@api_view(['POST'])
def create_image(request):
    if request.method == 'POST':
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

