from django.utils import timezone

from rest_framework import serializers
from .models import Release, Patch, Product, Image, Jar, HighLevelScope, SecurityIssue, PatchJar, PatchHighLevelScope, PatchProductImage,PatchImage,ProductSecurityIssue,PatchProductHelmChart,ReleaseProductImage

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



class PatchContextSecurityIssueSerializer(serializers.ModelSerializer):
    """
    Serializes a SecurityIssue and adds 'product_security_des' from the
    through-model 'ProductSecurityIssue' based on the patch/product context.
    """
    product_security_des = serializers.SerializerMethodField()

    class Meta:
        model = SecurityIssue
        fields = [
            "cve_id", "cvss_score", "severity", "affected_libraries",
            "library_path", "description",
            "created_at", "updated_at", "is_deleted",
            "product_security_des"  
        ]

    def get_product_security_des(self, obj):
        # 'obj' is the SecurityIssue instance.
        # We retrieve the patch and product from the context passed down.
        patch = self.context.get('patch')
        product = self.context.get('product')

        if not patch or not product:
            return ""

        try:
            psi = ProductSecurityIssue.objects.get(
                patch=patch,
                product=product,
                security_issue=obj
            )
            return psi.product_security_des
        except ProductSecurityIssue.DoesNotExist:
            return ""


class ImageSerializer(serializers.ModelSerializer):
    security_issues = PatchContextSecurityIssueSerializer(many=True, read_only=True)

    # Write-only field
    security_issue_ids = serializers.SlugRelatedField(
        many=True,
        write_only=True,
        slug_field='id',
        queryset=SecurityIssue.objects.filter(is_deleted=False)
    )

    class Meta:
        model = Image
        fields = [
            'product', 'image_name', 'build_number', 'release_date',
            'twistlock_report_url', 'twistlock_report_clean',
            'created_at', 'updated_at', 'is_deleted', 'size', 'layers',
            'security_issues',
            'security_issue_ids',
        ]

    # create/update methods 
    def create(self, validated_data):
        issue_ids = validated_data.pop('security_issue_ids', [])
        image = super().create(validated_data)
        image.security_issues.set(issue_ids)
        return image

    def update(self, instance, validated_data):
        issue_ids = validated_data.pop('security_issue_ids', None)
        image = super().update(instance, validated_data)
        if issue_ids is not None:
            image.security_issues.set(issue_ids)
        return image


# class ProductSerializer(serializers.ModelSerializer):
#     images = serializers.SerializerMethodField()
#     helm_charts = serializers.SerializerMethodField()

#     class Meta:
#         model = Product
#         fields = [
#             'name', 'images', 'status', 'created_at', 'updated_at',
#             'is_deleted', 'helm_charts'
#         ]

#     def get_helm_charts(self, obj):
#         # 'obj' is the Product instance
#         patch = self.context.get('patch')
#         if not patch:
#             return None
#         try:
#             helm_entry = PatchProductHelmChart.objects.get(patch=patch, product=obj)
#             return helm_entry.helm_charts
#         except PatchProductHelmChart.DoesNotExist:
#             return None

#     def get_images(self, obj):
#         # 'obj' is the Product instance
#         patch = self.context.get('patch')
#         if not patch:
#             return []

#         # Filter images for this product that belong to the current patch
#         images_for_patch = obj.images.filter(
#             build_number=patch.name,
#             is_deleted=False
#         )

#         # Build a new context for the ImageSerializer to have access to the product
#         new_context = self.context.copy()
#         new_context['product'] = obj

#         # Serialize the filtered images using the updated context
#         images_data = ImageSerializer(
#             images_for_patch, many=True, context=new_context
#         ).data

#         # Inject additional patch-specific data into each image object
#         for image_data in images_data:
#             try:
#                 patch_image = PatchImage.objects.get(
#                     patch=patch,
#                     image__image_name=image_data['image_name'],
#                     image__product=obj
#                 )
#                 image_data.update({
#                     "ot2_pass": patch_image.ot2_pass,
#                     "registry": patch_image.registry,
#                     "patch_build_number": patch_image.patch_build_number,
#                 })
#             except PatchImage.DoesNotExist:
#                 # Ensure fields are present even if no PatchImage record exists
#                 image_data.update({
#                     "ot2_pass": None, "registry": None, "patch_build_number": None
#                 })
#         return images_data

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    helm_charts = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'name', 'images', 'status', 'created_at', 'updated_at',
            'is_deleted', 'helm_charts'
        ]

    def get_helm_charts(self, obj):
      
        patch = self.context.get('patch')
        if not patch:
            return None 
        try:
            helm_entry = PatchProductHelmChart.objects.get(patch=patch, product=obj)
            return helm_entry.helm_charts
        except PatchProductHelmChart.DoesNotExist:
            return None

    def get_images(self, obj):
     
        patch = self.context.get('patch')

        if patch:
            images_for_patch = obj.images.filter(
                build_number=patch.name,
                is_deleted=False
            )

         
            new_context = self.context.copy()
            new_context['product'] = obj

            images_data = ImageSerializer(
                images_for_patch, many=True, context=new_context
            ).data

            for image_data in images_data:
                try:
                    patch_image = PatchImage.objects.get(
                        patch=patch,
                        image__image_name=image_data['image_name'],
                        image__product=obj
                    )
                    image_data.update({
                        "ot2_pass": patch_image.ot2_pass,
                        "registry": patch_image.registry,
                        "patch_build_number": patch_image.patch_build_number,
                    })
                except PatchImage.DoesNotExist:
                    image_data.update({
                        "ot2_pass": None, "registry": None, "patch_build_number": None
                    })
            return images_data

        else:
            all_images = obj.images.filter(is_deleted=False)

            new_context = {'product': obj}
            images_data = ImageSerializer(
                all_images, many=True, context=new_context
            ).data
            return images_data

class PatchJarSerializer(serializers.ModelSerializer):
    name    = serializers.CharField(source='jar.name', read_only=True)
    # version = serializers.CharField(source='jar.version', read_only=True)
    version = serializers.CharField(read_only=True)
    remarks = serializers.CharField()

    class Meta:
        model  = PatchJar
        fields = ('name', 'version', 'remarks', 'updated')

class PatchHighLevelScopeSerializer(serializers.ModelSerializer):
    name    = serializers.CharField(source='scope.name', read_only=True)
    version = serializers.CharField( read_only=True)
    remarks = serializers.CharField()

    class Meta:
        model  = PatchHighLevelScope
        fields = ('name', 'version', 'remarks')

class PatchImageNestedSerializer(serializers.ModelSerializer):
    image = ImageSerializer(read_only=True)
    image_name = serializers.CharField(write_only=True) 
    ot2_pass = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    registry = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    patch_build_number = serializers.CharField(allow_null=True, allow_blank=True, required=False)


    class Meta:
        model = PatchImage 
        fields = [
            'image', 
            'image_name' ,        
            'ot2_pass',       
            'registry',
            'patch_build_number',
        ]

class ProductHelmChartsSerializer(serializers.ModelSerializer):
    helm_charts = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    class Meta:
        model = PatchProductHelmChart  # your Product model
        fields = ['helm_charts']  # add more fields if needed


class ProductNestedSerializer(serializers.Serializer):
    name = serializers.CharField()
    # helm_charts = ProductHelmChartsSerializer(many=True)  
    helm_charts = serializers.CharField(allow_null=True, allow_blank=True, required=False)  # single string
    images = PatchImageNestedSerializer(many=True)


class PatchSerializer(serializers.ModelSerializer):
    jars = PatchJarSerializer(source='patchjar_set', many=True, read_only=True)
    scopes = PatchHighLevelScopeSerializer(source='patchhighlevelscope_set', many=True, read_only=True)

    jars_data = serializers.ListField(child=serializers.DictField(), write_only=True)
    scopes_data = serializers.ListField(child=serializers.DictField(), write_only=True)
    products_data = ProductNestedSerializer(many=True, write_only=True)

    products = serializers.SerializerMethodField()

    class Meta:
        model = Patch
        fields = [
            'name', 'release', 'release_date', 'kick_off', 'code_freeze',
            'platform_qa_build', 'client_build_availability',
            'description', 'patch_state',
            'kba', 'functional_fixes', 'security_issues',
            'jars', 'scopes',
            'jars_data', 'scopes_data', 'products_data',
            'products',
        ]
        lookup_field = 'name'
        extra_kwargs = {
            'jars_data': {'required': True},
            'scopes_data': {'required': True},
            'products_data': {'required': True},
        }

    def create(self, validated_data):
        jars_payload = validated_data.pop('jars_data', [])
        scopes_payload = validated_data.pop('scopes_data', [])
        products_payload = validated_data.pop('products_data', [])
        initial_products_data = self.initial_data.get('products_data', [])

        patch = super().create(validated_data)

        # Create Products, Images, and Helm Charts from validated data
        for pd in products_payload:
            pkg, _ = Product.objects.get_or_create(name=pd['name'])
            patch.products.add(pkg)
            if (helm_charts_value := pd.get('helm_charts')) is not None:
                PatchProductHelmChart.objects.update_or_create(
                    patch=patch, product=pkg, defaults={"helm_charts": helm_charts_value}
                )

            # for img_dict in pd['images']:
            #     img_name = img_dict.get('image_name')
            #       # Use get_or_create to AVOID overwriting existing Twistlock data.
            #     img, created = Image.objects.get_or_create(
            #         product=pkg,
            #         image_name=img_name,
            #         build_number=patch.name,
            #         defaults={
            #             'release_date': patch.release_date,
            #             'is_deleted': False,
            #             'twistlock_report_url': None,
            #             'twistlock_report_clean': None,
            #         }
            #     )
            #     # If the image already existed but was marked as deleted, un-delete it.
            #     if not created and img.is_deleted:
            #         img.is_deleted = False
            #         img.save(update_fields=['is_deleted'])

            #     PatchProductImage.objects.get_or_create(patch=patch, product=pkg, image=img)
            #     PatchImage.objects.update_or_create(
            #         patch=patch, image=img,
            #         defaults={
            #             'ot2_pass': img_dict.get('ot2_pass'), 'registry': img_dict.get('registry'),
            #             'patch_build_number': img_dict.get('patch_build_number'),
            #         }
            #     )
            for img_dict in pd['images']:
                img_name = img_dict.get('image_name')
                existing_img = Image.objects.filter(image_name=img_name).first()

                if existing_img:
                    # Always create a new image with fresh twistlock fields
                    img, created = Image.objects.get_or_create(
                        product=pkg,
                        image_name=img_name,
                        build_number=patch.name,
                        defaults={
                            'release_date': patch.release_date,
                            "is_deleted": False,
                            "twistlock_report_url": None,
                            "twistlock_report_clean": None,
                        }
                    )
                    if not created:
                        img.twistlock_report_url = None
                        img.twistlock_report_clean = None
                        img.is_deleted = False
                        img.save()

                else:
                    # New image – also ensure twistlock fields are null
                    img = Image.objects.create(
                        product=pkg,
                        image_name=img_name,
                        build_number=patch.name,
                        release_date= patch.release_date ,
                        twistlock_report_url=None,
                        twistlock_report_clean=None,
                        is_deleted=False,
                    )


                # Create PatchProductImage (basic linking)
                PatchProductImage.objects.get_or_create(
                    patch=patch,
                    product=pkg,
                    image=img
                )

                # Create or update PatchImage with extra patch-specific fields
                PatchImage.objects.update_or_create(
                    patch=patch,
                    image=img,
                    defaults={
                        'ot2_pass': img_dict.get('ot2_pass'),
                        'registry': img_dict.get('registry'),
                        'patch_build_number': img_dict.get('patch_build_number'),
                    }
                )
        # 4. Process security issues from the raw initial data payload
        for pd_raw in initial_products_data:
            pkg = Product.objects.get(name=pd_raw['name'])
            for img_dict in pd_raw.get('images', []):
                for issue in img_dict.get('security_issues', []):
                    cve_id = issue.get('cve_id')
                    product_security_des = issue.get('product_security_des')

                    if cve_id:
                        security_issue_obj, _ = SecurityIssue.objects.get_or_create(
                            cve_id=cve_id,
                            defaults={
                                'cvss_score': issue.get('cvss_score'), 'severity': issue.get('severity'),
                                'affected_libraries': issue.get('affected_libraries'),
                                'library_path': issue.get('library_path'), 'description': issue.get('description'),
                                'is_deleted': issue.get('is_deleted', False),
                            }
                        )
                        # Create the through-model link with the description
                        ProductSecurityIssue.objects.update_or_create(
                            patch=patch, product=pkg, security_issue=security_issue_obj,
                            defaults={'product_security_des': product_security_des}
                        )

        # Process Jars and Scopes 
        for jd in jars_payload:
            jar_obj, _ = Jar.objects.get_or_create(name=jd['name'])
            PatchJar.objects.update_or_create(
                patch=patch, jar=jar_obj, defaults={'version': jd.get('version'), 'remarks': jd.get('remarks', '')}
            )
        for sd in scopes_payload:
            scope_obj, _ = HighLevelScope.objects.get_or_create(name=sd['name'])
            PatchHighLevelScope.objects.update_or_create(
                patch=patch, scope=scope_obj, defaults={'version': sd.get('version'), 'remarks': sd.get('remarks', '')}
            )
        return patch



    # def update(self, instance, validated_data):
    #     # Pop all  payloads.
    #     jars_payload = validated_data.pop('jars_data', None)
    #     scopes_payload = validated_data.pop('scopes_data', None)
    #     products_payload = validated_data.pop('products_data', None)

    #     # Get the raw request data, which is our single source of truth for user intent.
    #     products_initial = self.initial_data.get('products_data', [])

    #     # Update the simple fields on the Patch model itself.
    #     patch = super().update(instance, validated_data)

    #     is_structural_change = False
    #     if products_initial:
          
    #         for pd_raw in products_initial:
    #             if "helm_charts" in pd_raw or "images" not in pd_raw:
    #                 is_structural_change = True
    #                 break
    #             for img_dict in pd_raw.get("images", []):
    #                 # If an image dict has more than just 'security_issues' it's a structural change.
    #                 if any(key not in ['security_issues', 'image_name'] for key in img_dict):
    #                      is_structural_change = True
    #                      break
    #             if is_structural_change:
    #                 break

    #     if products_payload is not None and is_structural_change:
    #         ProductSecurityIssue.objects.filter(patch=patch).delete()
    #         PatchImage.objects.filter(patch=patch).delete()
    #         PatchProductImage.objects.filter(patch=patch).delete()
    #         PatchProductHelmChart.objects.filter(patch=patch).delete()
    #         patch.products.clear()
            
    #         # Rebuild from scratch using the same logic as create()
    #         for pd_raw in products_initial:
    #             pkg, _ = Product.objects.get_or_create(name=pd_raw['name'])
    #             patch.products.add(pkg)
    #             if (helm_charts_value := pd_raw.get('helm_charts')) is not None:
    #                 PatchProductHelmChart.objects.create(patch=patch, product=pkg, helm_charts=helm_charts_value)
    #             for img_dict in pd_raw.get('images', []):
    #                 if not (img_name := img_dict.get('image_name')): continue
    #                 existing_img = Image.objects.filter(image_name=img_name).first()

    #                 if existing_img and existing_img.build_number != patch.name:
    #                     # Create new image with new build_number
    #                     img, created = Image.objects.get_or_create(
    #                         product=pkg,
    #                         image_name=img_name,
    #                         build_number=patch.name,
    #                         defaults={
    #                             'is_deleted': False,
    #                             'release_date': patch.release_date
    #                         }
    #                     )
    #                     # Your original code reset these fields, so we do the same.
    #                     img.twistlock_report_url = None
    #                     img.twistlock_report_clean = None
    #                     img.save()

    #                 elif existing_img and existing_img.build_number == patch.name:
    #                     # Use the existing one, update if needed
    #                     existing_img.is_deleted = False
    #                     existing_img.save()
    #                     img = existing_img

    #                 else:
    #                     # No existing image at all – ensure twistlock fields are null
    #                     img = Image.objects.create(
    #                         product=pkg,
    #                         image_name=img_name,
    #                         build_number=patch.name,
    #                         release_date=patch.release_date,
    #                         is_deleted=False,
    #                         twistlock_report_url=None,
    #                         twistlock_report_clean=None,
    #                     )

    #                 # Link product image to patch
    #                 PatchProductImage.objects.update_or_create(
    #                     patch=patch,
    #                     product=pkg,
    #                     image=img
    #                 )

    #                 # Create or update PatchImage with the provided metadata
    #                 PatchImage.objects.update_or_create(
    #                     patch=patch,
    #                     image=img,
    #                     defaults={
    #                         'ot2_pass': img_dict.get('ot2_pass'),
    #                         'registry': img_dict.get('registry'),
    #                         'patch_build_number': img_dict.get('patch_build_number'),
    #                     }
    #                 )
                    
    #                 for issue in img_dict.get('security_issues', []):
    #                     if (cve_id := issue.get('cve_id')):
    #                         product_security_des = issue.get('product_security_des')
    #                         security_issue_obj, _ = SecurityIssue.objects.get_or_create(cve_id=cve_id, defaults={'description': issue.get('description')})
    #                         ProductSecurityIssue.objects.update_or_create(patch=patch, product=pkg, security_issue=security_issue_obj, product_security_des=product_security_des)
        
    #     elif products_initial: 
    #         for pd_raw in products_initial:
    #             try:
    #                 product_obj = patch.products.get(name=pd_raw['name'])
    #             except Product.DoesNotExist:
    #                 continue # Skip products not on the patch

    #             for img_dict in pd_raw.get('images', []):
    #                 for issue in img_dict.get('security_issues', []):
    #                     if (cve_id := issue.get('cve_id')):
    #                         description = issue.get('product_security_des')
    #                         try:
    #                             # security_issue_obj = SecurityIssue.objects.get(cve_id=cve_id)
    #                             security_issue_obj = SecurityIssue.objects.filter(
    #                                 cve_id=cve_id,
    #                                 images__product=product_obj,
    #                                 images__patchproductimage__patch=patch # This makes it even more specific to the patch
    #                             ).distinct().first() 

    #                             if not security_issue_obj:
    #                                 # This CVE is not associated with this product in this patch. 
    #                                 print(f"Warning: Could not find SecurityIssue {cve_id} for product {product_obj.name} in patch {patch.name}")
    #                                 continue
    #                             ProductSecurityIssue.objects.update_or_create(
    #                                 patch=patch, product=product_obj, security_issue=security_issue_obj,
    #                                 defaults={'product_security_des': description}
    #                             )
    #                         except SecurityIssue.DoesNotExist:
    #                             continue # Skip unknown CVEs

    #     # --- Jars and Scopes  ---
    #     if jars_payload is not None:
    #         kept_jars = [jd['name'] for jd in jars_payload]
    #         PatchJar.objects.filter(patch=patch).exclude(jar__name__in=kept_jars).delete()
    #         for jd in jars_payload:
    #             jar_obj, _ = Jar.objects.get_or_create(name=jd['name'])
    #             PatchJar.objects.update_or_create(patch=patch, jar=jar_obj, defaults={'version': jd.get('version'), 'remarks': jd.get('remarks', '')})

    #     if scopes_payload is not None:
    #         kept = [sd['name'] for sd in scopes_payload]
    #         PatchHighLevelScope.objects.filter(patch=patch).exclude(scope__name__in=kept).delete()
    #         for sd in scopes_payload:
    #             scope_obj, _ = HighLevelScope.objects.get_or_create(name=sd['name'])
    #             PatchHighLevelScope.objects.update_or_create(patch=patch, scope=scope_obj, defaults={'version': sd.get('version'), 'remarks': sd.get('remarks', '')})

    #     return patch
    def update(self, instance, validated_data):
        # Pop nested payloads
        jars_payload = validated_data.pop('jars_data', None)
        scopes_payload = validated_data.pop('scopes_data', None)
        products_payload = validated_data.pop('products_data', None)

        # Keep original request for intent
        products_initial = self.initial_data.get('products_data', [])

        # Update Patch simple fields
        patch = super().update(instance, validated_data)

        # Handle products_images minimal payload
        if products_payload is not None:
            for pd in products_payload:
                # Ensure product exists and is linked
                pkg, _ = Product.objects.get_or_create(name=pd['name'])
                patch.products.add(pkg)

                for img_data in pd.get('images', []):
                    image_name = img_data.get('image_name')
                    if not image_name:
                        continue

                     # Lookup by both image_name and build_number
                    img, created = Image.objects.get_or_create(
                        image_name=image_name,
                        build_number=patch.name,
                        defaults={
                            'product': pkg,
                            'release_date': patch.release_date,
                            'is_deleted': False,
                            'twistlock_report_url': None,
                            'twistlock_report_clean': None,
                        }
                    )
            
                    # Ensure a single PatchImage exists
                    PatchImage.objects.get_or_create(
                        patch=patch,
                        image=img,
                        defaults={
                            'patch_build_number': patch.name,
                            'ot2_pass': None,
                            'registry': None,
                        }
                    )

        # Handle jars_payload
        if jars_payload is not None:
            kept_jars = [jar['name'] for jar in jars_payload]
            PatchJar.objects.filter(patch=patch).exclude(jar__name__in=kept_jars).delete()
            for jd in jars_payload:
                jar_obj, _ = Jar.objects.get_or_create(name=jd['name'])
                PatchJar.objects.update_or_create(
                    patch=patch,
                    jar=jar_obj,
                    defaults={'version': jd.get('version'), 'remarks': jd.get('remarks', '')}
                )

        # Handle scopes_payload
        if scopes_payload is not None:
            kept_scopes = [s['name'] for s in scopes_payload]
            PatchHighLevelScope.objects.filter(patch=patch).exclude(scope__name__in=kept_scopes).delete()
            for sd in scopes_payload:
                scope_obj, _ = HighLevelScope.objects.get_or_create(name=sd['name'])
                PatchHighLevelScope.objects.update_or_create(
                    patch=patch,
                    scope=scope_obj,
                    defaults={'version': sd.get('version'), 'remarks': sd.get('remarks', '')}
                )

        return patch

    def get_products(self, obj):
        patch = obj
        products_qs = obj.products.filter(is_deleted=False)

        # Serialize products with context so nested serializers can use 'patch'
        serializer = ProductSerializer(
            products_qs,
            many=True,
            context={'patch': patch}
        )
        products_data = serializer.data

        # Add patch-specific fields to each image in each product,
        # but *only for images matching the current patch build_number*
        for product_data in products_data:
            product_name = product_data['name']

            # helm charts
            try:
                helm_entry = PatchProductHelmChart.objects.get(
                    patch=patch,
                    product__name=product_name
                )
                product_data['helm_charts'] = helm_entry.helm_charts
            except PatchProductHelmChart.DoesNotExist:
                product_data['helm_charts'] = None
            # Filter images to only those with build_number == patch.name
            filtered_images = [
                img for img in product_data['images']
                if img.get('build_number') == patch.name
            ]
            # Replace original images with filtered list
            product_data['images'] = filtered_images

            for image_data in filtered_images:
                img_name = image_data['image_name']
                try:
                    patch_image = PatchImage.objects.get(
                        patch=patch,
                        image__image_name=img_name,
                        image__product__name=product_name
                    )
                    image_data.update({
                        "ot2_pass": patch_image.ot2_pass,
                        "registry": patch_image.registry,
                        "patch_build_number": patch_image.patch_build_number,
                    })
                except PatchImage.DoesNotExist:
                    pass

        return products_data


class ReleaseProductImageSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = ReleaseProductImage
        fields = '__all__'