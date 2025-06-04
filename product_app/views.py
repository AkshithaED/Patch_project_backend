from rest_framework.response import Response
from django.db import transaction
from rest_framework import viewsets, status, serializers
from .models import Release, Patch, Product, Image, Jar, HighLevelScope, SecurityIssue, PatchProductImage, PatchProductJar, PatchJar
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


@api_view(['GET'])
def patch_product_completion_status(request, name):
    try:
        patch = Patch.objects.get(name=name, is_deleted=False)
    except Patch.DoesNotExist:
        return Response({"error": "Patch not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = PatchSerializer(patch)
    patch_data = serializer.data

    completed_products = []
    incomplete_products = []

    for product in patch_data.get('products', []):
        total_images = 0
        completed_images = 0

        for image in product.get('images', []):
            total_images += 1
            if image.get('registry') and image.get('registry').lower() == 'released':
                completed_images += 0.5
            if image.get('ot2_pass') and image.get('ot2_pass').lower() == 'released':
                completed_images += 0.5

        if total_images == 0:
            incomplete_products.append(product)
        elif completed_images == total_images:
            completed_products.append(product)
        else:
            incomplete_products.append(product)

    return Response({
        "completed_products": completed_products,
        "incomplete_products": incomplete_products
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@transaction.atomic
def update_patch_data(request):

    data = request.data

    # 1) Look up the Patch by name
    patch_name = data.get("name")
    if not patch_name:
        return Response(
            {"error": "Field 'name' is required at top level."},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        patch = Patch.objects.get(name=patch_name, is_deleted=False)
        # print("patch  : ", patch)
    except Patch.DoesNotExist:
        return Response(
            {"error": f"Patch '{patch_name}' not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2) Iterate over each product in the payload
    for prod_data in data.get("products", []):
        product_name = prod_data.get("name")
        if not product_name:
            return Response(
                {"error": "Each product object must have a 'name'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(name=product_name, is_deleted=False)
        except Product.DoesNotExist:
            return Response(
                {"error": f"Product '{product_name}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2.a) Process Jars → get_or_create + overwrite only keys provided
        # for jar_data in prod_data.get("jars", []):
        #     jar_name = jar_data.get("name")
        #     if not jar_name:
        #         continue

        #     #  2.a.i) Ensure the Jar exists (or create it if missing)
        #     jar_obj, _ = Jar.objects.get_or_create(name=jar_name)



        #     try:
        #         existing_patchjar = PatchJar.objects.get(patch=patch, jar=jar_obj)
        #         default_version = existing_patchjar.version
        #     except PatchJar.DoesNotExist:
        #         default_version = None

        #     #  2.a.ii) Get or create the PatchProductJar for (patch, product, jar)
        #     ppj, created = PatchProductJar.objects.get_or_create(
        #         patch=patch,
        #         product=product,
        #         jar=jar_obj,
        #         defaults={
        #             # If they didn’t send curr_version/updated/version/remarks,
        #             # these defaults only apply on creation. On update, we'll override if keys exist.
        #             "current_version": jar_data.get("curr_version", None),
        #             "updated": jar_data.get("updated", False),
        #             "version": default_version or jar_data.get("version", None),
        #             "remarks": jar_data.get("remarks", "")
        #         }
        #     )

        #     if not created:
        #         # The row already existed → only overwrite fields that arrived in JSON
        #         if "curr_version" in jar_data:
        #             ppj.current_version = jar_data["curr_version"]
        #         if "updated" in jar_data:
        #             ppj.updated = jar_data["updated"]
        #         if "version" in jar_data:
        #             ppj.version = jar_data["version"]
        #         if "remarks" in jar_data:
        #             ppj.remarks = jar_data["remarks"]
        #         ppj.save()

        # 2.b) Process Images → upsert only the fields present
        helm_charts_val = prod_data.get("helm_charts", None)

        for img_data in prod_data.get("images", []):
            image_name = img_data.get("image_name")
            if not image_name:
                continue

            #  2.b.i) Try to fetch an existing Image for this product
            try:
                image = Image.objects.get(image_name=image_name, product=product)
                # Overwrite only the fields they provided
                if "build_number" in img_data:
                    image.build_number = img_data["build_number"]
                if "twistlock_report_url" in img_data:
                    image.twistlock_report_url = img_data["twistlock_report_url"]
                if "twistlock_report_clean" in img_data:
                    image.twistlock_report_clean = img_data["twistlock_report_clean"]
                image.save()
            except Image.DoesNotExist:
                # Create a brand-new Image row, with defaults for missing keys
                create_kwargs = {
                    "product": product,
                    "image_name": image_name,
                    "build_number": img_data.get("build_number", ""),
                    "twistlock_report_url": img_data.get("twistlock_report_url", ""),
                    "twistlock_report_clean": img_data.get("twistlock_report_clean", True),
                }
                image = Image.objects.create(**create_kwargs)

            #  2.b.ii) Upsert nested SecurityIssue rows if any were sent
            if "security_issues" in img_data:
                issue_objs = []
                for issue_data in img_data["security_issues"]:
                    cve_id = issue_data.get("cve_id")
                    if not cve_id:
                        continue

                    defaults = {}
                    if "cvss_score" in issue_data:
                        defaults["cvss_score"] = issue_data["cvss_score"]
                    if "severity" in issue_data:
                        defaults["severity"] = issue_data["severity"]
                    if "affected_libraries" in issue_data:
                        defaults["affected_libraries"] = issue_data["affected_libraries"]
                    if "library_path" in issue_data:
                        defaults["library_path"] = issue_data["library_path"]
                    # Always clear any “is_deleted” flag
                    defaults["is_deleted"] = False

                    issue_obj, _ = SecurityIssue.objects.update_or_create(
                        cve_id=cve_id,
                        defaults=defaults
                    )
                    issue_objs.append(issue_obj)

                # Replace the image’s M2M set with exactly what they sent
                image.security_issues.set(issue_objs)

            #  2.b.iii) Upsert (patch, image) → PatchImage, but only on the fields given
            patch_image_defaults = {}
            if "ot2_pass" in img_data:
                patch_image_defaults["ot2_pass"] = img_data["ot2_pass"]
            if "registry" in img_data:
                patch_image_defaults["registry"] = img_data["registry"]
            if helm_charts_val is not None:
                patch_image_defaults["helm_charts"] = helm_charts_val

            # Only call update_or_create if at least one of those three keys was in JSON
            if patch_image_defaults:
                PatchImage.objects.update_or_create(
                    patch=patch,
                    image=image,
                    defaults=patch_image_defaults
                )
            # Otherwise, leave any existing PatchImage row untouched

    return Response({"status": "success"}, status=status.HTTP_200_OK)