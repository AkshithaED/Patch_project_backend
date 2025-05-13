from venv import logger
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

from django.conf import settings

default_patch_data = settings.DEFAULTS['patch']


# -----------------------
# Standard ViewSets
# -----------------------
class ReleaseViewSet(viewsets.ModelViewSet):
    queryset = Release.objects.filter(is_deleted=False)
    serializer_class = ReleaseSerializer
    permission_classes = [ReleasePermission]
 
class PatchViewSet(viewsets.ModelViewSet):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer
    permission_classes = [PatchPermission]
    lookup_field = 'name'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            patch = serializer.save()

            related_products = request.data.get('related_products', [])
            product_images = request.data.get('product_images', [])

            for product_name in related_products:
                product = Product.objects.get(name=product_name)
                patch.related_products.add(product)

            for image_name in product_images:
                image = Image.objects.get(image_name=image_name)
                for product in patch.related_products.all():
                    product.images.add(image)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        patch = self.get_object()
        serializer = self.get_serializer(patch, data=request.data, partial=True)  # partial=True allows partial updates
        if serializer.is_valid():
            patch = serializer.save()

            # Update related products if provided
            related_products = request.data.get('related_products')
            if related_products is not None:
                patch.related_products.clear()
                for product_name in related_products:
                    product = Product.objects.get(name=product_name)
                    patch.related_products.add(product)

            # Update product images if provided
            product_images = request.data.get('product_images')
            if product_images is not None:
                patch.product_images.clear()
                for image_name in product_images:
                    image = Image.objects.get(image_name=image_name)
                    patch.product_images.add(image)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        patch = self.get_object()
        patch.related_products.clear()
        patch.delete()
        return Response(
            {"detail": "Patch deleted permanently."},
            status=status.HTTP_204_NO_CONTENT
        )


 
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
 

class SoftDeletePatchView(APIView):
    def delete(self, request, pk):
        try:
            patch = Patch.objects.get(name=pk)
            patch.soft_delete()
            return Response({"detail": "Patch deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Patch.DoesNotExist:
            return Response({"detail": "Patch not found."}, status=status.HTTP_404_NOT_FOUND)


class UpdatePatchView(APIView):
    permission_classes = [PatchPermission]

    def put(self, request, pk):
        try:
            patch = Patch.objects.get(name=pk)
        except Patch.DoesNotExist:
            return Response({"detail": "Patch not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatchSerializer(patch, data=request.data, partial=False)
        if serializer.is_valid():
            patch = serializer.save()

            # Update related products if provided
            related_products = request.data.get('related_products')
            if related_products is not None:
                patch.related_products.clear()
                for product_name in related_products:
                    product = Product.objects.get(name=product_name)
                    patch.related_products.add(product)

            # Update product images if provided
            product_images = request.data.get('product_images')
            if product_images is not None:
                patch.product_images.clear()
                for image_name in product_images:
                    image = Image.objects.get(image_name=image_name)
                    patch.product_images.add(image)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            patch = Patch.objects.get(name=pk)
        except Patch.DoesNotExist:
            return Response({"detail": "Patch not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatchSerializer(patch, data=request.data, partial=True)
        if serializer.is_valid():
            patch = serializer.save()

            related_products = request.data.get('related_products')
            if related_products is not None:
                patch.related_products.clear()
                for product_name in related_products:
                    product = Product.objects.get(name=product_name)
                    patch.related_products.add(product)

            product_images = request.data.get('product_images')
            if product_images is not None:
                patch.product_images.clear()
                for image_name in product_images:
                    image = Image.objects.get(image_name=image_name)
                    patch.product_images.add(image)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
