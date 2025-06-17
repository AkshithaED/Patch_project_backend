from rest_framework.response import Response
from django.db import transaction
from rest_framework import viewsets, status, serializers
from .models import Release, Patch, Product, Image, Jar, HighLevelScope, SecurityIssue, PatchProductImage, PatchProductJar, PatchJar, PatchImage, PatchProductHelmChart
from .serializers import ReleaseSerializer, PatchSerializer, ProductSerializer, ImageSerializer, SecurityIssueSerializer, JarSerializer, HighLevelScopeSerializer
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .data import PATCH_DATA, build_image_url


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
    # queryset = Product.objects.filter(is_deleted=False, is_helm_chart=False)
    serializer_class = ProductSerializer
    lookup_field = 'name'

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.filter(is_deleted=False)
    serializer_class = ImageSerializer

    def get_object(self):
        image_name = self.kwargs['image_name']
        build_number = self.kwargs['build_number']
        return get_object_or_404(Image, image_name=image_name, build_number=build_number, is_deleted=False)


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

#api for completion percentage of patch
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
    # for jar in patch_data.get('jars', []):
    #     total_items += 1
    #     if jar.get('updated') is True:
    #         completed_items += 1
    #     elif jar.get('remarks'):  # updated == False but has remarks
    #         completed_items += 1

    #  Check product images
    for product in patch_data.get('products', []):

         #  Count JARs via PatchProductJar
        ppj_qs = PatchProductJar.objects.filter(
            patch_jar_id__patch=patch,
            product=product.get('name')
        )
        for ppj in ppj_qs:
            total_items += 1
            # Completed if updated=True or non‐empty remarks
            if ppj.updated or (ppj.remarks and ppj.remarks.strip() != ""):
                completed_items += 1

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
        total_items = 0
        completed_items = 0

        # --- Count JARs via PatchProductJar ---
        ppj_qs = PatchProductJar.objects.filter(
            patch_jar_id__patch=patch,
            product=product.get('name')
        )
        for ppj in ppj_qs:
            total_items += 1
            if ppj.updated or (ppj.remarks and ppj.remarks.strip() != ""):
                completed_items += 1

        # --- Count image status ---
        for image in product.get('images', []):
            total_items += 1  # Each image counts as 1 unit (0.5 + 0.5)
            if image.get('registry') and image.get('registry').lower() == 'released':
                completed_items += 0.5
            if image.get('ot2_pass') and image.get('ot2_pass').lower() == 'released':
                completed_items += 0.5

        if total_items == 0:
            # Nothing to track means incomplete
            incomplete_products.append(product)
        elif completed_items == total_items:
            completed_products.append(product)
        else:
            incomplete_products.append(product)

    return Response({
        "completed_products": completed_products,
        "incomplete_products": incomplete_products
    }, status=status.HTTP_200_OK)



#api for populating tables in database
@api_view(['POST'])
@transaction.atomic
def update_patch_data(request):

    data = request.data
    for patch_data in data:
        # 1) Look up the Patch by name
        patch_name = patch_data.get("name")
        if not patch_name:
            return Response(
                {"error": "Field 'name' is required at top level."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            patch = Patch.objects.get(name=patch_name, is_deleted=False)
        except Patch.DoesNotExist:
            return Response(
                {"error": f"Patch '{patch_name}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2) Iterate over each product in the payload
        for prod_data in patch_data.get("products", []):
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

            #
            # 2.a) Process “jars” for this (patch, product) → write into PatchProductJar
            #
            for jar_data in prod_data.get("jars", []):  # ← new block
                jar_name = jar_data.get("name")
                if not jar_name:
                    continue

                #  2.a.i) Ensure the Jar exists (or create it if missing)
                jar_obj, _ = Jar.objects.get_or_create(name=jar_name)

                #  2.a.ii) Find the existing PatchJar for (this patch, this jar),
                #            so we can pull its “version” field:
                try:
                    patch_jar = PatchJar.objects.get(patch=patch, jar=jar_obj)
                except PatchJar.DoesNotExist:
                    # If there is no PatchJar row yet, we can either:
                    #  • create a default one with version = None, or skip.
                    patch_jar = PatchJar.objects.create(patch=patch, jar=jar_obj, version=None, remarks="")
                
                #  2.a.iii) Now, upsert the PatchProductJar row.
                defaults = {}

                # If the payload sent “curr_version”, overwrite current_version:
                if "curr_version" in jar_data:
                    defaults["current_version"] = jar_data.get("curr_version")
                else:
                    # Optionally: do nothing, leave existing current_version alone.
                    pass

                # Always set “version” from the PatchJar row (so they stay in sync):
                # defaults["version"] = patch_jar.version

                # If payload sent “updated” or “remarks”, copy them over:
                if "updated" in jar_data:
                    defaults["updated"] = jar_data["updated"]
                if "remarks" in jar_data:
                    defaults["remarks"] = jar_data["remarks"]

                # Upsert PatchProductJar:
                ppj, created = PatchProductJar.objects.update_or_create(
                    patch_jar_id=patch_jar,  # this is a ForeignKey to PatchJar
                    product=product,
                    defaults=defaults
                )
                # At this point, you have either created or updated the (
                #    patch_jar_id = patch_jar, product = product
                # ) row, with default values set above.

            #
            # 2.b) Process “images” for this (patch, product)
            #      (update Image fields, PatchImage fields, and attach SecurityIssues)

            for img_data in prod_data.get("images", []):
                image_name = img_data.get("image_name")
                if not image_name:
                    continue

                #  2.b.i) Try to fetch an existing Image for this product
                try:
                    # image = Image.objects.get(image_name=image_name, product=product)
                    image = Image.objects.get(image_name=image_name, build_number=patch_name)
                    # Overwrite only the fields they provided:
                    # if "build_number" in img_data:
                    #     image.build_number = img_data["build_number"]
                    if "twistlock_report_url" in img_data:
                        image.twistlock_report_url = img_data["twistlock_report_url"]
                    if "twistlock_report_clean" in img_data:
                        image.twistlock_report_clean = img_data["twistlock_report_clean"]
                    image.save()
                except Image.DoesNotExist:
                    # If no existing Image, create one with defaults
                    create_kwargs = {
                        "product": product,
                        "image_name": image_name,
                        "build_number": img_data.get("patch_name", ""),
                        "twistlock_report_url": img_data.get("twistlock_report_url", ""),
                        "twistlock_report_clean": img_data.get("twistlock_report_clean", True),
                    }
                    image = Image.objects.create(**create_kwargs)

                #
                #  2.b.ii) Upsert nested SecurityIssue rows if any were sent
                #
                if "security_issues" in img_data:
                    issue_objs = []
                    for issue_data in img_data["security_issues"]:
                        # We match or create by the four fields (cve_id, cvss_score, severity, affected_libraries).
                        # After creating/fetching, we will attach it to image.security_issues M2M.
                        cve_id = issue_data.get("CVE")
                        cvss_score = issue_data.get("cvss")
                        severity = issue_data.get("Severity")
                        affected_libraries = issue_data.get("PackageName")

                        if not (cve_id and cvss_score is not None and severity and affected_libraries):
                            # Skip incomplete entries
                            continue

                        # Build the “lookup” dict (the four‐field key) and “defaults” dict for any extra fields:
                        lookup = {
                            "cve_id": cve_id,
                            "cvss_score": cvss_score,
                            "severity": severity,
                            "affected_libraries": affected_libraries
                        }
                        defaults = {
                            "library_path": issue_data.get("library_path", ""),
                            "description": issue_data.get("Description", ""),
                            "is_deleted": False,
                        }

                        issue_obj, _ = SecurityIssue.objects.update_or_create(
                            **lookup,
                            defaults=defaults
                        )
                        issue_objs.append(issue_obj)

                    # Replace the image’s M2M set with exactly what they sent:
                    image.security_issues.set(issue_objs)

                #
                #  2.b.iii) Upsert (patch, image) → PatchImage, only on the fields given
                #
                patch_image_defaults = {}
                if "ot2_pass" in img_data:
                    patch_image_defaults["ot2_pass"] = img_data["ot2_pass"]
                if "registry" in img_data:
                    patch_image_defaults["registry"] = img_data["registry"]
                # if "helm_charts" in img_data:
                #     patch_image_defaults["helm_charts"] = img_data["helm_charts"]
                if "build_number" in img_data:
                    patch_image_defaults["patch_build_number"] = img_data["build_number"]

                if patch_image_defaults:
                    # update_or_create PatchImage row for (patch, image)
                    PatchImage.objects.update_or_create(
                        patch=patch,
                        image=image,
                        defaults=patch_image_defaults
                    )
                # If no patch_image_defaults were provided, we leave any existing PatchImage untouched.

            # 2.c) Upsert PatchProductHelmChart
            helm_val = prod_data.get("helm_charts", None)
            if helm_val is not None:
                PatchProductHelmChart.objects.update_or_create(
                    patch=patch,
                    product=product,
                    defaults={"helm_charts": helm_val}
                )
        # End of “for each product” loop

    return Response({"status": "success"}, status=status.HTTP_200_OK)

# API to get product specific jars
@api_view(['GET'])
def patch_product_jars_list(request, patch_name, product_name):
    # patch_name = request.query_params.get('patch_name')
    # product_name = request.query_params.get('product_name')

    if not patch_name or not product_name:
        return Response(
            {"error": "Both 'patch_name' and 'product_name' query parameters are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 1) Verify patch exists
    try:
        patch = Patch.objects.get(name=patch_name, is_deleted=False)
    except Patch.DoesNotExist:
        return Response(
            {"error": f"Patch '{patch_name}' not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2) Verify product exists
    try:
        product = Product.objects.get(name=product_name, is_deleted=False)
    except Product.DoesNotExist:
        return Response(
            {"error": f"Product '{product_name}' not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 3) Fetch all PatchProductJar rows for (patch, product)
    ppj_qs = PatchProductJar.objects.filter(
        patch_jar_id__patch=patch,
        product=product
    )

    # 4) Build response array
    jars_list = []
    for ppj in ppj_qs:
        pj = ppj.patch_jar_id  # the related PatchJar instance
        jar_dict = {
            "name": pj.jar.name,
            "version": pj.version,
            "current_version": ppj.current_version,
            "remarks": ppj.remarks,
            "updated": ppj.updated,
        }
        jars_list.append(jar_dict)

    return Response({"jars": jars_list}, status=status.HTTP_200_OK)

#API for updating patchproductjars
@api_view(['PATCH'])
def update_patch_product_jar(request, patch_name, product_name, jar_name):
    # 1) Look up the Patch
    try:
        patch = Patch.objects.get(name=patch_name, is_deleted=False)
    except Patch.DoesNotExist:
        return Response(
            {"error": f"Patch '{patch_name}' not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2) Look up the Product
    try:
        product = Product.objects.get(name=product_name, is_deleted=False)
    except Product.DoesNotExist:
        return Response(
            {"error": f"Product '{product_name}' not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 3) Look up the Jar
    try:
        jar = Jar.objects.get(name=jar_name)
    except Jar.DoesNotExist:
        return Response(
            {"error": f"Jar '{jar_name}' not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 4) Find the matching PatchJar (patch, jar)
    try:
        patch_jar = PatchJar.objects.get(patch=patch, jar=jar)
    except PatchJar.DoesNotExist:
        return Response(
            {"error": f"No PatchJar found for patch '{patch_name}' and jar '{jar_name}'."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 5) Find the single PatchProductJar row for (patch_jar, product)
    try:
        ppj = PatchProductJar.objects.get(patch_jar_id=patch_jar, product=product)
    except PatchProductJar.DoesNotExist:
        return Response(
            {
              "error": (
                f"No PatchProductJar found for patch='{patch_name}', "
                f"product='{product_name}', jar='{jar_name}'."
              )
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # 6) Update only fields provided in JSON
    data = request.data
    updated = False

    if "remarks" in data:
        ppj.remarks = data["remarks"]
        updated = True

    if "updated" in data:
        ppj.updated = data["updated"]
        updated = True

    if updated:
        ppj.save()
        return Response(
            {"status": "success", "remarks": ppj.remarks, "updated": ppj.updated},
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"error": "No updatable fields ('remarks' or 'updated') provided."},
            status=status.HTTP_400_BAD_REQUEST
        )


#api for getting path
@api_view(['POST'])
def build_image_url_endpoint(request):
    payload = request.data
    # Validate presence of the four keys
    for key in ("release", "product", "image", "registry"):
        if key not in payload:
            return Response(
                {"error": f"Missing '{key}'"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    rel     = payload["release"]
    prod    = payload["product"]
    img     = payload["image"]
    registry= payload["registry"]

    try:
        # 1) Fetch the entry from the nested dict:
        server_entry = PATCH_DATA[rel][prod][img][registry]
    except KeyError:
        return Response(
            {"error": "No entry found for the given keys in PATCH_DATA."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2) Call your URL‐builder and return its result
    url_payload = build_image_url(server_entry)
    return Response(url_payload, status=status.HTTP_200_OK)