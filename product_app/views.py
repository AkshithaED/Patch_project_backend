from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django.shortcuts import get_list_or_404, get_object_or_404

from .models import Release, Patch, Product, Image, SecurityIssue
from .serializers import (
    ReleaseSerializer, PatchSerializer, ProductSerializer,
    ImageSerializer, SecurityIssueSerializer
)
from .permissions import *

# -----------------------
# Standard ViewSets
# -----------------------
class ReleaseViewSet(viewsets.ModelViewSet):
    queryset = Release.objects.filter(is_deleted=False)
    serializer_class = ReleaseSerializer
    permission_classes = [ReleasePermission]


class PatchViewSet(viewsets.ModelViewSet):
    queryset = Patch.objects.filter(is_deleted=False)
    serializer_class = PatchSerializer
    permission_classes = [PatchPermission]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    permission_classes = [ProductPermission]


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.filter(is_deleted=False)
    serializer_class = ImageSerializer
    permission_classes = [ImagePermission]


class SecurityIssueViewSet(viewsets.ModelViewSet):
    queryset = SecurityIssue.objects.filter(is_deleted=False)
    serializer_class = SecurityIssueSerializer
    permission_classes = [SecurityIssuePermission]

# -----------------------
# Nested Views
# -----------------------
class NestedPatchListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, release_name):
        release = get_object_or_404(Release, name=release_name)
        patches = release.patches.filter(is_deleted=False)
        serializer = PatchSerializer(patches, many=True)
        return Response(serializer.data)


class NestedProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, release_name, patch_name):
        release = get_object_or_404(Release, name=release_name)
        patch = get_object_or_404(Patch, name=patch_name, release=release, is_deleted=False)
        products = patch.related_products.filter(is_deleted=False)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class NestedImageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, release_name, patch_name, product_name):
        product = get_object_or_404(Product, name=product_name, is_deleted=False)
        images = product.images.filter(is_deleted=False)
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data)


class SecurityIssueByImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, release_name, patch_name, product_name, build_number):
        images = get_list_or_404(
            Image,
            product__name=product_name,
            build_number=build_number,
            is_deleted=False
        )

        # All images are clean
        if all(img.twistlock_report_clean for img in images):
            return Response({'status': 'Clean'}, status=status.HTTP_200_OK)

        all_issues = []
        for img in images:
            issues = img.security_issues.filter(is_deleted=False)
            serializer = SecurityIssueSerializer(issues, many=True)
            all_issues.extend(serializer.data)

        return Response(all_issues)

# -----------------------
# Custom Create View for Images
# -----------------------
@api_view(['POST'])
def create_image(request):
    if not (request.user.is_staff or request.user.role in ['product_owner', 'product_manager']):
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = ImageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
