from rest_framework.response import Response
from django.db import transaction
from rest_framework import viewsets, status, serializers
from .models import Release, Patch, Product, Image, Jar, HighLevelScope, SecurityIssue, PatchProductImage
from .serializers import ReleaseSerializer, PatchSerializer, ProductSerializer, ImageSerializer, SecurityIssueSerializer, JarSerializer, HighLevelScopeSerializer

class ReleaseViewSet(viewsets.ModelViewSet):
    queryset = Release.objects.filter(is_deleted=False)
    serializer_class = ReleaseSerializer
    lookup_field = 'name' 

class PatchViewSet(viewsets.ModelViewSet):
    queryset = Patch.objects.filter(is_deleted=False)
    serializer_class = PatchSerializer
    lookup_field = 'name'
    def create(self, request, *args, **kwargs):
        data = request.data
        products_data = data.pop('products_data', [])

        if not products_data:
            return Response({'error': 'products_data is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                patch_serializer = self.get_serializer(data=data)
                patch_serializer.is_valid(raise_exception=True)
                patch = patch_serializer.save()

                for prod_data in products_data:
                    product_name = prod_data.get('name')
                    image_names = prod_data.get('images', [])

                    if not product_name or not image_names:
                        raise serializers.ValidationError("Each product must have at least one image.")

                    try:
                        product = Product.objects.get(name=product_name)
                    except Product.DoesNotExist:
                        raise serializers.ValidationError(f"Product '{product_name}' not found.")

                    patch.products.add(product)

                    for image_name in image_names:
                        try:
                            image = Image.objects.get(image_name=image_name, product=product)
                        except Image.DoesNotExist:
                            raise serializers.ValidationError(f"Image '{image_name}' not found for product '{product_name}'.")

                        # Link patch, product, and image
                        PatchProductImage.objects.create(patch=patch, product=product, image=image)
                # return Response(self.get_serializer(patch).data, status=status.HTTP_201_CREATED)
                response_data = self.get_serializer(patch).data
                # Manually adding products_data
                products_data = []
                for product in patch.products.all():
                    image_names = Image.objects.filter(
                        product=product,
                        patchproductimage__patch=patch
                    ).values_list('image_name', flat=True)

                    products_data.append({
                        'name': product.name,
                        'images': list(image_names)
                    })

                response_data['products_data'] = products_data
                return Response(response_data, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     patch_list = []

    #     for patch in queryset:
    #         base_data = PatchSerializer(patch).data
    #         products_data = []

    #         for product in patch.products.filter(is_deleted=False):
    #             images = patch.images.filter(
    #                 patchproductimage__patch=patch,
    #                 patchproductimage__product=product,
    #                 is_deleted=False
    #             ).distinct()

    #             products_data.append({
    #                 "name": product.name,
    #                 "images": [img.image_name for img in images]
    #             })

    #         base_data['products_data'] = products_data
    #         patch_list.append(base_data)

    #     return Response(patch_list)
    
    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     response_data = serializer.data

    #     # Add products_data manually
    #     products_data = []
    #     for product in instance.products.all():
    #         image_names = Image.objects.filter(
    #             product=product,
    #             patchproductimage__patch=instance
    #         ).values_list('image_name', flat=True)

    #         products_data.append({
    #             'name': product.name,
    #             'images': list(image_names)
    #         })

    #     response_data['products_data'] = products_data
    #     return Response(response_data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        patch_list = []

        for patch in queryset:
            base_data = PatchSerializer(patch).data
            products_data = []

            for product in patch.products.filter(is_deleted=False):
                images = patch.images.filter(
                    patchproductimage__patch=patch,
                    patchproductimage__product=product,
                    is_deleted=False
                ).distinct()
                image_data = ImageSerializer(images, many=True).data
                products_data.append({
                    "name": product.name,
                    "images": image_data
                })

            base_data['products_data'] = products_data
            patch_list.append(base_data)

        return Response(patch_list)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = serializer.data

        # Add products_data manually
        products_data = []
        for product in instance.products.all():
            images = instance.images.filter(
                patchproductimage__patch=instance,
                patchproductimage__product=product,
                is_deleted=False
            ).distinct()
            image_data = ImageSerializer(images, many=True).data
            products_data.append({
                'name': product.name,
                'images': image_data
            })

        response_data['products_data'] = products_data
        return Response(response_data)

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
