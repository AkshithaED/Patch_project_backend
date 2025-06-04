
from rest_framework import serializers
from .models import Release, Patch, Product, Image, Jar, HighLevelScope, SecurityIssue, PatchJar, PatchHighLevelScope, PatchProductImage,PatchImage,ProductSecurityIssue

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


# class ProductSecurityIssueSerializer(serializers.ModelSerializer):
#     product_security_des = serializers.SerializerMethodField()

#     class Meta:
#         model = SecurityIssue
#         fields = [
#             "cve_id", "cvss_score", "severity", "affected_libraries",
#             "library_path", "description", "product_security_des",
#             "created_at", "updated_at", "is_deleted"
#         ]
#     def get_product_security_des(self, security_issue):
#         product = self.context.get('product')
#         patch = self.context.get('patch')
#         if not product or not patch:
#             return ""

#         try:
#             psi = ProductSecurityIssue.objects.get(
#                 product=product,
#                 security_issue=security_issue,
#                 patch=patch,
#             )
#             return psi.product_security_des
#         except ProductSecurityIssue.DoesNotExist:
#             print(f"Missing PSI for product {product} patch {patch} issue {security_issue.cve_id}")
#             return ""

class ProductSecurityIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityIssue
        fields = [
            "cve_id", "cvss_score", "severity", "affected_libraries",
            "library_path", "description",
            "created_at", "updated_at", "is_deleted"
        ]


# class ImageSerializer(serializers.ModelSerializer):
#     security_issues = serializers.SerializerMethodField()
#     security_issue_ids = serializers.SlugRelatedField(
#         many=True,
#         write_only=True,
#         slug_field='cve_id',
#         queryset=SecurityIssue.objects.filter(is_deleted=False)
#     )

#     class Meta:
#         model = Image
#         fields = [
#             'product', 'image_name', 'build_number', 'release_date',
#             'twistlock_report_url', 'twistlock_report_clean',
#             'created_at', 'updated_at', 'is_deleted',
#             'security_issues', 'security_issue_ids'
#         ]
#     # def get_security_issues(self, obj):
#     #     product = obj.product
#     #     patch = self.context.get("patch")
#     #     security_issues = obj.security_issues.filter(is_deleted=False)

#     #     serializer = SecurityIssueWithProductDescSerializer(
#     #         security_issues,
#     #         many=True,
#     #         context={'product': product, 'patch': patch}
#     #     )
#     #     return serializer.data
#     # def get_security_issues(self, obj):
#     #     security_issues = obj.security_issues.filter(is_deleted=False)
#     #     serializer = SecurityIssueWithProductDescSerializer(security_issues, many=True)
#     #     return serializer.data

     

#     def create(self, validated_data):
#         issue_ids = validated_data.pop('security_issue_ids', [])
#         image = super().create(validated_data)
#         image.security_issues.set(issue_ids)
#         return image

#     def update(self, instance, validated_data):
#         issue_ids = validated_data.pop('security_issue_ids', None)
#         image = super().update(instance, validated_data)
#         # if issue_ids is not None:
#         #     image.security_issues.set(issue_ids)
#         return image

class ImageSerializer(serializers.ModelSerializer):
    # 1) Nested, read-only display of full SecurityIssue objects
    security_issues = SecurityIssueSerializer(many=True, read_only=True)

    # 2) Write-only field to accept CVE IDs when posting/patching
    security_issue_ids = serializers.SlugRelatedField(
        many=True,
        write_only=True,
        slug_field='cve_id',
        queryset=SecurityIssue.objects.filter(is_deleted=False)
    )

    class Meta:
        model = Image
        fields = [
            'product', 'image_name', 'build_number', 'release_date',
            'twistlock_report_url', 'twistlock_report_clean',
            'created_at', 'updated_at', 'is_deleted',
            # both of these together:
            'security_issues',     # read nested
            'security_issue_ids',  # write only
        ]

    def create(self, validated_data):
        # Pop off the IDs, then assign normally
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
#     images = ImageSerializer(many=True, read_only=True)
#     security_issues = serializers.SerializerMethodField()

#     class Meta:
#         model = Product
#         fields = ['name', 'images', 'status', 'created_at', 'updated_at', 'is_deleted', 'security_issues']

#     def get_security_issues(self, obj):
#         patch = self.context.get('patch')
#         if not patch:
#             return []

#         security_issues_qs = SecurityIssue.objects.filter(
#             productsecurityissue__product=obj,
#             productsecurityissue__patch=patch,
#             is_deleted=False
#         ).distinct()

#         serializer = ProductSecurityIssueSerializer(
#             security_issues_qs,
#             many=True,
#             context={'product': obj, 'patch': patch}
#         )
#         return serializer.data
class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
        # security_issues = serializers.SerializerMethodField()
    product_security_des = serializers.SerializerMethodField()  # Add this line

    class Meta:
        model = Product
        fields = [
            'name', 'images', 'status', 'created_at', 'updated_at', 
            'is_deleted', 'product_security_des'
        ]

    def get_security_issues(self, obj):
        patch = self.context.get('patch')
        if not patch:
            return []

        security_issues_qs = SecurityIssue.objects.filter(
            productsecurityissue__product=obj,
            productsecurityissue__patch=patch,
            is_deleted=False
        ).distinct()

        serializer = ProductSecurityIssueSerializer(
            security_issues_qs,
            many=True,
            context={'product': obj, 'patch': patch}
        )
        return serializer.data

    def get_product_security_des(self, obj):
        patch = self.context.get('patch')
        if not patch:
            return ""

        psi = ProductSecurityIssue.objects.filter(product=obj, patch=patch).first()
        if psi:
            return psi.product_security_des
        return ""


class PatchJarSerializer(serializers.ModelSerializer):
    name    = serializers.CharField(source='jar.name', read_only=True)
    version = serializers.CharField(source='jar.version', read_only=True)
    remarks = serializers.CharField()

    class Meta:
        model  = PatchJar
        fields = ('name', 'version', 'remarks', 'updated')

class PatchHighLevelScopeSerializer(serializers.ModelSerializer):
    name    = serializers.CharField(source='scope.name', read_only=True)
    version = serializers.CharField(source='scope.version', read_only=True)
    remarks = serializers.CharField()

    class Meta:
        model  = PatchHighLevelScope
        fields = ('name', 'version', 'remarks')

class PatchImageNestedSerializer(serializers.ModelSerializer):
    image = ImageSerializer(read_only=True)
    image_name = serializers.CharField(write_only=True) 
    ot2_pass = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    registry = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    helm_charts = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    patch_build_number = serializers.CharField(allow_null=True, allow_blank=True, required=False)


    class Meta:
        model = PatchImage 
        fields = [
            'image', 
            'image_name' ,        
            'ot2_pass',       
            'registry',
            'helm_charts',
            'patch_build_number',
        ]




class ProductNestedSerializer(serializers.Serializer):
    name = serializers.CharField()
    images = PatchImageNestedSerializer(many=True)


class PatchSerializer(serializers.ModelSerializer):
    # — read‐only through-model views —
    jars   = PatchJarSerializer(
                 source='patchjar_set', many=True, read_only=True
             )
    scopes = PatchHighLevelScopeSerializer(
                 source='patchhighlevelscope_set', many=True, read_only=True
             )

    # — write‐only payloads —
    jars_data     = serializers.ListField(
                        child=serializers.DictField(), write_only=True
                    )
    scopes_data   = serializers.ListField(
                        child=serializers.DictField(), write_only=True
                    )
    # products_data = serializers.ListField(
    #                     child=serializers.DictField(), write_only=True
    #                 )
    products_data = ProductNestedSerializer(many=True, write_only=True)


    # — read‐only nested output —
    products = serializers.SerializerMethodField()

    class Meta:
        model  = Patch
        fields = [
            'name', 'release', 'release_date', 'kick_off', 'code_freeze',
            'platform_qa_build', 'client_build_availability',
            'description', 'patch_state',
            # through-model read
            'jars', 'scopes',
            # write-only inputs
            'jars_data', 'scopes_data', 'products_data',
            # nested products read
            'products',
        ]
        lookup_field = 'name'
        extra_kwargs = {
            'jars_data':     {'required': True},
            'scopes_data':   {'required': True},
            'products_data': {'required': True},
        }

    def create(self, validated_data):
        # 1) Extract all three payloads
        jars_payload     = validated_data.pop('jars_data', [])
        scopes_payload   = validated_data.pop('scopes_data', [])
        products_payload = validated_data.pop('products_data', [])
        initial_products_data = self.initial_data.get('products_data', [])

        # 2) Create the Patch record
        patch = super().create(validated_data)

        for pd in products_payload:
            try:
                pkg = Product.objects.get(name=pd['name'])
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product '{pd['name']}' not found.")

            patch.products.add(pkg)

            for img_dict in pd['images']:
                img_name = img_dict.get('image_name')
                try:
                    img = Image.objects.get(image_name=img_name, product=pkg)
                except Image.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Image '{img_name}' for product '{pkg.name}' not found."
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
                        'helm_charts': img_dict.get('helm_charts'),
                        'patch_build_number': img_dict.get('patch_build_number'),
                    }
                )
                # print("initial_products_data",initial_products_data)

        for pd_raw in initial_products_data:
            pkg = Product.objects.get(name=pd_raw['name'])

            for img_dict in pd_raw.get('images', []):
                for issue in img_dict.get('security_issues', []):
                    cve_id = issue.get('cve_id')
                    product_security_des = issue.get('product_security_des')

                    if cve_id:
                        # Here you can get_or_create SecurityIssue safely
                        print(f"Fetching SecurityIssue with cve_id: '{cve_id}'")

                        security_issue_obj, created = SecurityIssue.objects.get_or_create(
                            cve_id=cve_id,
                            defaults={
                                'cvss_score': issue.get('cvss_score'),
                                'severity': issue.get('severity'),
                                'affected_libraries': issue.get('affected_libraries'),
                                'library_path': issue.get('library_path'),
                                'description': issue.get('description'),
                                'is_deleted': issue.get('is_deleted', False),
                            }
                        )
                    print("Before update_or_create call")
                    print(f"Patch pk: {patch.pk}, Product pk: {pkg.pk}, SecurityIssue pk: {security_issue_obj.pk}")
                    try:
                        psi_obj, created = ProductSecurityIssue.objects.update_or_create(
                            patch=patch,
                            product=pkg,
                            security_issue=security_issue_obj,
                            defaults={'product_security_des': product_security_des}
                        )
                        print(f"PSI {'created' if created else 'updated'}: {psi_obj}")
                    except Exception as e:
                        print("Error in update_or_create:", e)

        for jd in jars_payload:
            jar_obj, _ = Jar.objects.get_or_create(
                name=jd['name'],
                defaults={'version': jd.get('version')}
            )
            # update existing or create new PatchJar row
            PatchJar.objects.update_or_create(
                patch=patch,
                jar=jar_obj,
                defaults={'remarks': jd.get('remarks', '')}
            )

        # 5) Link scopes + remarks
        for sd in scopes_payload:
            scope_obj, _ = HighLevelScope.objects.get_or_create(
                name=sd['name'],
                defaults={'version': sd.get('version')}
            )
            # update existing or create new through‐row
            PatchHighLevelScope.objects.update_or_create(
                patch=patch,
                scope=scope_obj,
                defaults={'remarks': sd.get('remarks', '')}
            )

        return patch

    def update(self, instance, validated_data):
        # 1) Pop payloads if present
        jars_payload     = validated_data.pop('jars_data', None)
        scopes_payload   = validated_data.pop('scopes_data', None)
        products_payload = validated_data.pop('products_data', None)
        # products_payload = self.initial_data.get('products_data', [])

        # 2) Update the Patch fields
        patch = super().update(instance, validated_data)

        # 3) If products_data sent, clear & re-create
        if products_payload is not None:
            patch.products.clear()

            for pd in products_payload:
                pkg = Product.objects.get(name=pd['name'])
                patch.products.add(pkg)

                for img_dict in pd['images']:
                    img_name = img_dict.get('image_name')
                    if not img_name:
                        raise serializers.ValidationError(f"Missing or empty 'image_name' for product '{pd['name']}'")

                    # ✅ Now img is only set if img_name is valid
                    try:
                        img = Image.objects.get(image_name=img_name, product=pkg)
                    except Image.DoesNotExist:
                        raise serializers.ValidationError(f"Image '{img_name}' for product '{pd['name']}' not found.")

                    # Link product image to patch
                    PatchProductImage.objects.update_or_create(
                        patch=patch,
                        product=pkg,
                        image=img
                    )

                    # Create or update PatchImage with the provided metadata
                    PatchImage.objects.update_or_create(
                        patch=patch,
                        image=img,
                        defaults={
                            'ot2_pass': img_dict.get('ot2_pass'),
                            'registry': img_dict.get('registry'),
                            'helm_charts': img_dict.get('helm_charts'),
                            'patch_build_number': img_dict.get('patch_build_number'),
                        }
                    )

        products_initial = self.initial_data.get('products_data', [])

        for pd_raw in products_initial:
            try:
                pkg = Product.objects.get(name=pd_raw['name'])
            except Product.DoesNotExist:
                continue  # or handle error

            for img_dict in pd_raw.get('images', []):
                for issue in img_dict.get('security_issues', []):
                    cve_id = issue.get('cve_id')
                    product_security_des = issue.get('product_security_des')

                    if cve_id:
                        try:
                            security_issue_obj = SecurityIssue.objects.get(cve_id=cve_id)
                        except SecurityIssue.DoesNotExist:
                            continue  # or handle error

                        ProductSecurityIssue.objects.update_or_create(
                            patch=patch,
                            product=pkg,
                            security_issue=security_issue_obj,
                            defaults={'product_security_des': product_security_des}
                        )     



        if jars_payload is not None:
            # simply update_or_create each row; no need to clear
            for jd in jars_payload:
                jar_obj, _ = Jar.objects.get_or_create(
                    name=jd['name'],
                    defaults={'version': jd.get('version')}
                )
                PatchJar.objects.update_or_create(
                    patch=patch,
                    jar=jar_obj,
                    defaults={'remarks': jd.get('remarks', '')}
                )
            # And remove any jars *not* in the new payload:
            kept_jars = [ jd['name'] for jd in jars_payload ]
            PatchJar.objects.filter(
                patch=patch
            ).exclude(
                jar__name__in=kept_jars
            ).delete()

        # 5) If scopes_data sent, clear & re-create
        if scopes_payload is not None:
            # 1) Upsert each incoming scope
            for sd in scopes_payload:
                scope_obj, _ = HighLevelScope.objects.get_or_create(
                    name=sd['name'],
                    defaults={'version': sd.get('version')}
                )
                PatchHighLevelScope.objects.update_or_create(
                    patch=patch,
                    scope=scope_obj,
                    defaults={'remarks': sd.get('remarks', '')}
                )

            # 2) Remove any old scopes not in the new payload
            kept = [ sd['name'] for sd in scopes_payload ]
            PatchHighLevelScope.objects.filter(
                patch=patch
            ).exclude(
                scope__name__in=kept
            ).delete()

        return patch


    # def get_products(self, obj):
    #     patch = obj
    #     products_list = []
    #     products_qs = obj.products.filter(is_deleted=False)
    
    #     # Serialize products with context so nested serializers can use 'patch'
    #     serializer = ProductSerializer(
    #         products_qs,
    #         many=True,
    #         context={'patch': patch}
    #     )
    #     products_data = serializer.data

    #     for product in obj.products.filter(is_deleted=False):
    #         imgs = Image.objects.filter(
    #             product=product,
    #             patchproductimage__patch=obj,
    #             is_deleted=False
    #         ).distinct()

    #         images_data = []

    #         for img in imgs:
    #             image_serialized = ImageSerializer(img, context={'product': product, 'patch': patch}).data

    #             try:
    #                 patch_image = PatchImage.objects.get(patch=obj, image=img)
    #                 image_serialized.update({
    #                     "ot2_pass": patch_image.ot2_pass,
    #                     "registry": patch_image.registry,
    #                     "helm_charts": patch_image.helm_charts,
    #                     "patch_build_number": patch_image.patch_build_number,
    #                 })
    #             except PatchImage.DoesNotExist:
    #                 pass

    #             images_data.append(image_serialized)

    #         products_list.append({
    #             "name": product.name,
    #             "images": images_data
    #         })

    #     return products_list
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

        # Add patch-specific fields to each image in each product
        for product_data in products_data:
            product_name = product_data['name']
            for image_data in product_data['images']:
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
                        "helm_charts": patch_image.helm_charts,
                        "patch_build_number": patch_image.patch_build_number,
                    })
                except PatchImage.DoesNotExist:
                    pass

        return products_data
