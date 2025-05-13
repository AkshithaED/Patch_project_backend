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
    

def create(self, request, *args, **kwargs):
    # Serialize the incoming data
    serializer = self.get_serializer(data=request.data)
    if serializer.is_valid():
        # Create the patch instance
        patch = serializer.save()

        # Get the list of related products and images from request data
        related_products = request.data.get('related_products', [])
        product_images = request.data.get('product_images', [])

        # Associate products with the patch (Many-to-Many relation)
        for product_id in related_products:
            product = Product.objects.get(name=product_id)  # Use 'name' instead of 'id'
            patch.related_products.add(product)

        # Associate images with each product (Many-to-Many relation)
        for image_id in product_images:
            image = Image.objects.get(image_name=image_id)  # Ensure image exists
            # Iterate through the related products and add the image to each product
            for product in patch.related_products.all():
                product.images.add(image)  # Add the image to the product's image set

        # Return a response indicating the patch has been created and related data has been updated
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # If serializer data is not valid, return errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # Override destroy method to perform hard delete (remove from DB permanently)
    def destroy(self, request, *args, **kwargs):
        # Get the patch to be deleted
        patch = self.get_object()

        # Optionally, clear relationships before deleting (like disassociating products)
        patch.related_products.clear()

        # # Perform hard delete (permanent removal from DB)
        # patch.delete()

        # Return response confirming the patch has been deleted
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
            patch.delete()
            return Response({"detail": "Patch deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Patch.DoesNotExist:
            return Response({"detail": "Patch not found."}, status=status.HTTP_404_NOT_FOUND)

