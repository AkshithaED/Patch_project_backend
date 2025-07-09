from rest_framework.response import Response
from django.db import transaction
from rest_framework import viewsets, status, serializers
from .models import Release, Patch, Product, Image, Jar, HighLevelScope, SecurityIssue, PatchProductImage, PatchProductJar, PatchImageJar, PatchJar, PatchImage, PatchProductHelmChart,ProductJarRelease, ReleaseProductImage,ProductSecurityIssue,ReleaseProductImage
from .serializers import ReleaseSerializer, PatchSerializer, ProductSerializer, ImageSerializer, SecurityIssueSerializer, JarSerializer, HighLevelScopeSerializer,ReleaseProductImageSerializer
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .data import PATCH_DATA, build_image_url
from rest_framework.views import APIView
from .update_data import update_details
from rest_framework import generics
from rest_framework.generics import RetrieveUpdateAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
import requests 
from django.http import JsonResponse



class ReleaseViewSet(viewsets.ModelViewSet):
    queryset = Release.objects.filter(is_deleted=False)
    serializer_class = ReleaseSerializer
    lookup_field = 'name' 

class PatchViewSet(viewsets.ModelViewSet):
    queryset         = Patch.objects.filter(is_deleted=False)
    serializer_class = PatchSerializer
    lookup_field     = 'name'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response([serializer.data], status=status.HTTP_200_OK)

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
        patch = Patch.objects.get(name=name, is_deleted=False)
    except Patch.DoesNotExist:
        return Response({"error": "Patch not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = PatchSerializer(patch)
    patch_data = serializer.data

    total_items = 0
    completed_items = 0

    for product in patch_data.get('products', []):
        for image in product.get('images', []):

            # fetch the PatchImage row
            try:
                pi = PatchImage.objects.get(
                    patch=patch,
                    image__image_name=image.get('image_name')
                )
            except PatchImage.DoesNotExist:
                continue

            #  Half‐points from the PatchImage fields directly
            total_items += 1
            if (pi.registry or '').lower() == 'released':
                completed_items += 0.5

            if (pi.ot2_pass or '').lower() == 'released':
                completed_items += 0.5

            # now only count those jars where a PatchJar exists
            pij_qs = PatchImageJar.objects.filter(patch_image=pi)
            for pij in pij_qs:
                # skip if there's no matching PatchJar
                if not PatchJar.objects.filter(patch=patch, jar=pij.jar).exists():
                    continue

                total_items += 1
                if pij.updated or (pij.remarks and pij.remarks.strip()):
                    completed_items += 1

    if total_items == 0:
        return Response({"completion_percentage": 0}, status=status.HTTP_200_OK)

    percentage = round((completed_items / total_items) * 100, 2)
    return Response({"completion_percentage": percentage}, status=status.HTTP_200_OK)

#api for getting completed and incomplete products
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

        # --- image halves + jar counts per image ---
        for image in product.get('images', []):

            # fetch the PatchImage instance
            try:
                pi = PatchImage.objects.get(
                    patch=patch,
                    image__image_name=image.get('image_name')
                )
            except PatchImage.DoesNotExist:
                # no jars to count for this image
                continue

            #  Half‐points from the PatchImage fields directly
            total_items += 1
            if (pi.registry or '').lower() == 'released':
                completed_items += 0.5

            if (pi.ot2_pass or '').lower() == 'released':
                completed_items += 0.5

            # iterate PatchImageJar rows
            pij_qs = PatchImageJar.objects.filter(patch_image=pi)
            for pij in pij_qs:
                # only count if a matching PatchJar exists
                if not PatchJar.objects.filter(patch=patch, jar=pij.jar).exists():
                    continue

                total_items += 1
                if pij.updated or (pij.remarks and pij.remarks.strip()):
                    completed_items += 1

        if total_items > 0 and completed_items == total_items:
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
            # for jar_data in prod_data.get("jars", []):  # ← new block
            #     jar_name = jar_data.get("name")
            #     if not jar_name:
            #         continue

            #     #  2.a.i) Ensure the Jar exists (or create it if missing)
            #     jar_obj, _ = Jar.objects.get_or_create(name=jar_name)

            #     #  2.a.ii) Find the existing PatchJar for (this patch, this jar),
            #     #            so we can pull its “version” field:
            #     try:
            #         patch_jar = PatchJar.objects.get(patch=patch, jar=jar_obj)
            #     except PatchJar.DoesNotExist:
            #         # If there is no PatchJar row yet, we can either:
            #         #  • create a default one with version = None, or skip.
            #         patch_jar = PatchJar.objects.create(patch=patch, jar=jar_obj, version=None, remarks="")
                
            #     #  2.a.iii) Now, upsert the PatchProductJar row.
            #     defaults = {}

            #     # If the payload sent “curr_version”, overwrite current_version:
            #     if "curr_version" in jar_data:
            #         defaults["current_version"] = jar_data.get("curr_version")
            #     else:
            #         # Optionally: do nothing, leave existing current_version alone.
            #         pass

            #     # Always set “version” from the PatchJar row (so they stay in sync):
            #     # defaults["version"] = patch_jar.version

            #     # If payload sent “updated” or “remarks”, copy them over:
            #     if "updated" in jar_data:
            #         defaults["updated"] = jar_data["updated"]
            #     if "remarks" in jar_data:
            #         defaults["remarks"] = jar_data["remarks"]

            #     # Upsert PatchProductJar:
            #     ppj, created = PatchProductJar.objects.update_or_create(
            #         patch_jar_id=patch_jar,  # this is a ForeignKey to PatchJar
            #         product=product,
            #         defaults=defaults
            #     )
            #     # At this point, you have either created or updated the (
            #     #    patch_jar_id = patch_jar, product = product
            #     # ) row, with default values set above.

            # #
            # # 2.b) Process “images” for this (patch, product)
            # #      (update Image fields, PatchImage fields, and attach SecurityIssues)

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
                # patch_image_defaults = {}
                # if "ot2_pass" in img_data:
                #     patch_image_defaults["ot2_pass"] = img_data["ot2_pass"]
                # if "registry" in img_data:
                #     patch_image_defaults["registry"] = img_data["registry"]
                # # if "helm_charts" in img_data:
                # #     patch_image_defaults["helm_charts"] = img_data["helm_charts"]
                # if "build_number" in img_data:
                #     patch_image_defaults["patch_build_number"] = img_data["build_number"]

                # if patch_image_defaults:
                #     # update_or_create PatchImage row for (patch, image)
                #     PatchImage.objects.update_or_create(
                #         patch=patch,
                #         image=image,
                #         defaults=patch_image_defaults
                #     )

                # -- fetch or create PatchImage
                patch_image, _ = PatchImage.objects.update_or_create(
                    patch=patch,
                    image=image,
                    defaults={
                        **({"ot2_pass": img_data["ot2_pass"]} if "ot2_pass" in img_data else {}),
                        **({"registry": img_data["registry"]} if "registry" in img_data else {}),
                        # **({"patch_build_number": img_data["build_number"]} if "build_number" in img_data else {}),
                         # only update build_number when we’re _not_ already locked
                        **({
                            "patch_build_number": img_data["build_number"]
                        } if (
                            "build_number" in img_data and
                            not PatchImage.objects.filter(
                                patch=patch, image=image, lock=True
                            ).exists()
                        ) else {}),

                        # force lock on any new “Released” status
                        **(
                            {"lock": True}
                            if img_data.get("ot2_pass") == "Released"
                            or img_data.get("registry") == "Released"
                            else {}
                        ),
                    }
                )

                # — NEW: process jars nested under this image —
                for jar_data in img_data.get("jars", []):
                    jar_name = jar_data.get("Name")
                    if not jar_name:
                        continue

                    # 1) auto-create the Jar if missing
                    jar_obj, _ = Jar.objects.get_or_create(name=jar_name)

                    # 2) build the fields for PatchImageJar (no 'version' field here)
                    pjij_defaults = {
                        **({"current_version": jar_data["Version"]} if "Version" in jar_data else {}),
                        **({"updated": jar_data["updated"]} if "updated" in jar_data else {}),
                        **({"remarks": jar_data["remarks"]} if "remarks" in jar_data else {}),
                    }

                    # 3) upsert into PatchImageJar
                    PatchImageJar.objects.update_or_create(
                        patch_image=patch_image,
                        jar=jar_obj,
                        defaults=pjij_defaults
                    )
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

# # API to get product specific jars
# @api_view(['GET'])
# def patch_product_jars_list(request, patch_name, product_name):
#     # patch_name = request.query_params.get('patch_name')
#     # product_name = request.query_params.get('product_name')

#     if not patch_name or not product_name:
#         return Response(
#             {"error": "Both 'patch_name' and 'product_name' query parameters are required."},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     # 1) Verify patch exists
#     try:
#         patch = Patch.objects.get(name=patch_name, is_deleted=False)
#     except Patch.DoesNotExist:
#         return Response(
#             {"error": f"Patch '{patch_name}' not found."},
#             status=status.HTTP_404_NOT_FOUND
#         )

#     # 2) Verify product exists
#     try:
#         product = Product.objects.get(name=product_name, is_deleted=False)
#     except Product.DoesNotExist:
#         return Response(
#             {"error": f"Product '{product_name}' not found."},
#             status=status.HTTP_404_NOT_FOUND
#         )

#     # 3) Fetch all PatchProductJar rows for (patch, product)
#     ppj_qs = PatchProductJar.objects.filter(
#         patch_jar_id__patch=patch,
#         product=product
#     )

#     # 4) Build response array
#     jars_list = []
#     for ppj in ppj_qs:
#         pj = ppj.patch_jar_id  # the related PatchJar instance
#         jar_dict = {
#             "name": pj.jar.name,
#             "version": pj.version,
#             "current_version": ppj.current_version,
#             "remarks": ppj.remarks,
#             "updated": ppj.updated,
#         }
#         jars_list.append(jar_dict)

#     return Response({"jars": jars_list}, status=status.HTTP_200_OK)

# #API for updating patchproductjars
# @api_view(['PATCH'])
# def update_patch_product_jar(request, patch_name, product_name, jar_name):
#     # 1) Look up the Patch
#     try:
#         patch = Patch.objects.get(name=patch_name, is_deleted=False)
#     except Patch.DoesNotExist:
#         return Response(
#             {"error": f"Patch '{patch_name}' not found."},
#             status=status.HTTP_404_NOT_FOUND
#         )

#     # 2) Look up the Product
#     try:
#         product = Product.objects.get(name=product_name, is_deleted=False)
#     except Product.DoesNotExist:
#         return Response(
#             {"error": f"Product '{product_name}' not found."},
#             status=status.HTTP_404_NOT_FOUND
#         )

#     # 3) Look up the Jar
#     try:
#         jar = Jar.objects.get(name=jar_name)
#     except Jar.DoesNotExist:
#         return Response(
#             {"error": f"Jar '{jar_name}' not found."},
#             status=status.HTTP_404_NOT_FOUND
#         )

#     # 4) Find the matching PatchJar (patch, jar)
#     try:
#         patch_jar = PatchJar.objects.get(patch=patch, jar=jar)
#     except PatchJar.DoesNotExist:
#         return Response(
#             {"error": f"No PatchJar found for patch '{patch_name}' and jar '{jar_name}'."},
#             status=status.HTTP_404_NOT_FOUND
#         )

#     # 5) Find the single PatchProductJar row for (patch_jar, product)
#     try:
#         ppj = PatchProductJar.objects.get(patch_jar_id=patch_jar, product=product)
#     except PatchProductJar.DoesNotExist:
#         return Response(
#             {
#               "error": (
#                 f"No PatchProductJar found for patch='{patch_name}', "
#                 f"product='{product_name}', jar='{jar_name}'."
#               )
#             },
#             status=status.HTTP_404_NOT_FOUND
#         )

#     # 6) Update only fields provided in JSON
#     data = request.data
#     updated = False

#     if "remarks" in data:
#         ppj.remarks = data["remarks"]
#         updated = True

#     if "updated" in data:
#         ppj.updated = data["updated"]
#         updated = True

#     if updated:
#         ppj.save()
#         return Response(
#             {"status": "success", "remarks": ppj.remarks, "updated": ppj.updated},
#             status=status.HTTP_200_OK
#         )
#     else:
#         return Response(
#             {"error": "No updatable fields ('remarks' or 'updated') provided."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
# API to list all jars for a given patch & image
@api_view(['GET'])
def patch_image_jars_list(request, patch_name, image_name):
    # 1) Verify Patch
    try:
        patch = Patch.objects.get(name=patch_name, is_deleted=False)
    except Patch.DoesNotExist:
        return Response(
            {"error": f"Patch '{patch_name}' not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2) Verify Image
    try:
        image = Image.objects.get(image_name=image_name, build_number=patch_name)
    except Image.DoesNotExist:
        return Response(
            {"error": f"Image '{image_name}' not found for patch '{patch_name}'."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 3) Fetch PatchImage
    try:
        patch_image = PatchImage.objects.get(patch=patch, image=image)
    except PatchImage.DoesNotExist:
        return Response(
            {"jars": []},
            status=status.HTTP_200_OK
        )

    # 4) Fetch all PatchImageJar rows for this patch_image
    pij_qs = PatchImageJar.objects.filter(patch_image=patch_image)

    # 5) Build response list
    jars_list = []
    for pij in pij_qs:
        jars_list.append({
            "name": pij.jar.name,
            "current_version": pij.current_version,
            "remarks": pij.remarks,
            "updated": pij.updated,
        })

    return Response({"jars": jars_list}, status=status.HTTP_200_OK)


# API to update a single PatchImageJar entry
@api_view(['PATCH'])
def update_patch_image_jar(request, patch_name, image_name, jar_name):
    # 1) Verify Patch
    try:
        patch = Patch.objects.get(name=patch_name, is_deleted=False)
    except Patch.DoesNotExist:
        return Response(
            {"error": f"Patch '{patch_name}' not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2) Verify Image
    try:
        image = Image.objects.get(image_name=image_name, build_number=patch_name)
    except Image.DoesNotExist:
        return Response(
            {"error": f"Image '{image_name}' not found for patch '{patch_name}'."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 3) Fetch PatchImage
    try:
        patch_image = PatchImage.objects.get(patch=patch, image=image)
    except PatchImage.DoesNotExist:
        return Response(
            {"error": f"No PatchImage found for patch '{patch_name}' and image '{image_name}'."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 4) Verify Jar
    try:
        jar = Jar.objects.get(name=jar_name)
    except Jar.DoesNotExist:
        return Response(
            {"error": f"Jar '{jar_name}' not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 5) Fetch PatchImageJar
    try:
        pij = PatchImageJar.objects.get(patch_image=patch_image, jar=jar)
    except PatchImageJar.DoesNotExist:
        return Response(
            {"error": (
                f"No PatchImageJar entry for patch='{patch_name}', "
                f"image='{image_name}', jar='{jar_name}'."
            )},
            status=status.HTTP_404_NOT_FOUND
        )

    # 6) Update fields if provided
    data = request.data
    updated = False
    if "current_version" in data:
        pij.current_version = data["current_version"]
        updated = True
    if "remarks" in data:
        pij.remarks = data["remarks"]
        updated = True
    if "updated" in data:
        pij.updated = data["updated"]
        updated = True

    if not updated:
        return Response(
            {"error": "No updatable fields provided ('current_version', 'remarks', or 'updated')."},
            status=status.HTTP_400_BAD_REQUEST
        )

    pij.save()
    return Response(
        {
            "status": "success",
            "current_version": pij.current_version,
            "remarks": pij.remarks,
            "updated": pij.updated
        },
        status=status.HTTP_200_OK
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



def product_jar_release_list(request):
    data = ProductJarRelease.objects.all()
    return render(request, 'product_jar_release_list.html', {'data': data})

def release_product_image_list(request):
    data = ReleaseProductImage.objects.all()
    return render(request, 'release_product_image_list.html', {'data': data})


class PatchProductDetailView(APIView):
    def get(self, request, patch_name, product_name):
        try:
            patch = get_object_or_404(Patch, name=patch_name)

            if not patch.products.filter(name__iexact=product_name).exists():
                return Response(
                    {"error": f"Product '{product_name}' not found in patch '{patch_name}'"},
                    status=status.HTTP_404_NOT_FOUND
                )


            serializer = PatchSerializer(patch, context={'request': request})
            
            full_patch_data = serializer.data

            filtered_products = [
                product_data for product_data in full_patch_data.get('products', [])
                if product_data.get('name', '').lower() == product_name.lower()
            ]

            full_patch_data['products'] = filtered_products
            
            final_response = [full_patch_data]

            return Response(final_response, status=status.HTTP_200_OK)

        except Patch.DoesNotExist:
            return Response({"error": "Patch not found"}, status=status.HTTP_404_NOT_FOUND)




class PatchDetailView(APIView):
   
    def get(self, request, patch_name):
     
        patch = get_object_or_404(Patch, name=patch_name)

        serializer = PatchSerializer(patch, context={'request': request})

       
        return Response([serializer.data], status=status.HTTP_200_OK)



class RefDB(APIView):
    def get(self, request, patch_name=None, product_name=None):
        if not product_name or product_name.lower() in {"null", "none"}:
            product_name = None
 
        try:
            update_details(patch_name, product_name)
            patchdetailsview = PatchDetailView()
            response = patchdetailsview.get(request, patch_name)
            data = response.data
        except Exception as e:
            data = {"message": "Handled error", "error": str(e)}
 
        return Response(data, status=200)


class ReleaseProductImageListAPIView(RetrieveUpdateDestroyAPIView):
  
    serializer_class = ReleaseProductImageSerializer

    def get_object(self):
        release_name = self.kwargs.get('release_name')
        product_name = self.kwargs.get('product_name')
        image_name = self.kwargs.get('image_name')

        try:
            return ReleaseProductImage.objects.get(
                release__name=release_name,
                product__name=product_name,
                image_name=image_name
            )
        except ReleaseProductImage.DoesNotExist:
            raise NotFound("ReleaseProductImage not found.")

class AllReleaseProductImagesAPIView(ListCreateAPIView):
    queryset = ReleaseProductImage.objects.all()
    serializer_class = ReleaseProductImageSerializer


@api_view(['PATCH'])
def update_product_security_description(request, patch_name, product_name, cve_id):
    """
    Updates or creates the 'product_security_des' field for a specific 
    combination of a Patch, Product, and SecurityIssue. 
    """

    data = request.data
    if 'product_security_des' not in data:
        return Response(
            {"error": "The 'product_security_des' field is required in the request body."},
            status=status.HTTP_400_BAD_REQUEST
        )
    new_description = data['product_security_des']

    try:
       
        product_security_issue_entry = ProductSecurityIssue.objects.get(
            patch__name=patch_name,
            product__name=product_name,
            security_issue__cve_id=cve_id
        )
        
        product_security_issue_entry.product_security_des = new_description
        product_security_issue_entry.save(update_fields=['product_security_des'])
        
        status_code = status.HTTP_200_OK
        message = "Product security description updated successfully."

    except ProductSecurityIssue.DoesNotExist:
        try:
            patch = Patch.objects.get(name=patch_name)
            product = Product.objects.get(name=product_name)
                      
            security_issue = SecurityIssue.objects.filter(cve_id=cve_id).first()

            if not security_issue:
                raise SecurityIssue.DoesNotExist(f"No SecurityIssue found for cve_id='{cve_id}'")

            product_security_issue_entry = ProductSecurityIssue.objects.create(
                patch=patch,
                product=product,
                security_issue=security_issue,
                product_security_des=new_description
            )
            
            status_code = status.HTTP_201_CREATED 
            message = "Product security description entry created successfully."

        except (Patch.DoesNotExist, Product.DoesNotExist, SecurityIssue.DoesNotExist) as e:
            return Response(
                {"error": f"Cannot create entry because a required component is missing: {e}"},
                status=status.HTTP_404_NOT_FOUND
            )

    return Response(
        {
            "status": "success",
            "message": message,
            "entry": {
                "patch": patch_name,
                "product": product_name,
                "cve_id": cve_id,
                "product_security_des": product_security_issue_entry.product_security_des,
            }
        },
        status=status_code
    )

<<<<<<< HEAD
#Api for build number locking
@api_view(['PATCH'])
def toggle_lock_by_names(request):
    patch_name = request.data.get('patch')
    image_name = request.data.get('image')
    lock_val   = request.data.get('lock')

    # Validate required fields
    if not isinstance(patch_name, str) or not isinstance(image_name, str):
        return Response(
            {"detail": "'patch' and 'image' must be strings."},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not isinstance(lock_val, bool):
        return Response(
            {"detail": "'lock' must be a boolean."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Look up the related objects
    patch_obj = get_object_or_404(Patch, name=patch_name)
    image_obj = get_object_or_404(Image, image_name=image_name, build_number = patch_name)
    pi        = get_object_or_404(PatchImage, patch=patch_obj, image=image_obj)

    # Apply your rules
    if lock_val and not pi.lock:
        # false → true
        pi.lock = True
    elif not lock_val and pi.lock:
        # true → false
        pi.lock      = False
        pi.registry  = 'Not Released'
        pi.ot2_pass  = 'Not Released'
    # else: no change

    pi.save()
    # serializer = PatchImageSerializer(pi, context={'request': request})
    # return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({
        "lock":            pi.lock,
        "registry":        pi.registry,
        "ot2_pass":        pi.ot2_pass,
        "build_number":    pi.patch_build_number,
    }, status=status.HTTP_200_OK)
=======

class PatchesByProductView(APIView):
   

    def get(self, request, product_name, format=None):
      
        try:
            base_queryset = Patch.objects.filter(is_deleted=False)

            filtered_patches = base_queryset.filter(products__name__iexact=product_name).distinct()

            if not filtered_patches.exists():
                return Response(
                    {"detail": f"No patches found for product '{product_name}'."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = PatchSerializer(filtered_patches, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
          
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# NEW API VIEW for a single product's completion percentage in a patch
@api_view(['GET'])
def product_patch_completion_percentage(request, name, product_name):
    try:
        # Find the specific patch and product
        patch = Patch.objects.get(name=name, is_deleted=False)
        product_obj = Product.objects.get(name=product_name, is_deleted=False)
    except Patch.DoesNotExist:
        return Response({"error": "Patch not found."}, status=status.HTTP_404_NOT_FOUND)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    # Use the serializer to get the product's data within the context of the patch
    serializer = PatchSerializer(patch)
    patch_data = serializer.data

    # Find the specific product data from the serialized output
    target_product = None
    for p in patch_data.get('products', []):
        if p.get('name') == product_name:
            target_product = p
            break

    if not target_product:
        return Response({"error": f"Product '{product_name}' is not part of patch '{name}'."}, status=status.HTTP_404_NOT_FOUND)

    total_items = 0
    completed_items = 0

    # Loop through only the images of the target product
    for image in target_product.get('images', []):
        # Fetch the PatchImage row to get completion status
        try:
            pi = PatchImage.objects.get(
                patch=patch,
                image__image_name=image.get('image_name')
            )
        except PatchImage.DoesNotExist:
            continue

     
        total_items += 1
        if (pi.registry or '').lower() == 'released':
            completed_items += 0.5

        if (pi.ot2_pass or '').lower() == 'released':
            completed_items += 0.5
        
        # Get all Jars associated with this specific PatchImage
        pij_qs = PatchImageJar.objects.filter(patch_image=pi)
        
        for pij in pij_qs:
            # We only count this Jar towards the total if it's managed at the patch level
            if not PatchJar.objects.filter(patch=patch, jar=pij.jar).exists():
                continue

            total_items += 1
            # A jar is "complete" if it's marked as updated OR has remarks
            if pij.updated or (pij.remarks and pij.remarks.strip()):
                completed_items += 1

    if total_items == 0:
        # If there are no trackable items, completion is 0%
        return Response({"completion_percentage": 0}, status=status.HTTP_200_OK)

    percentage = round((completed_items / total_items) * 100, 2)
    return Response({"completion_percentage": percentage}, status=status.HTTP_200_OK)
>>>>>>> demo2
