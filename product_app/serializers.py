from django.utils import timezone

from rest_framework import serializers
from .models import Release, Patch, Product, Image, Jar, HighLevelScope, SecurityIssue, PatchJar, PatchHighLevelScope, PatchProductImage,PatchImage,ProductSecurityIssue,PatchProductHelmChart

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



class ProductSecurityIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityIssue
        fields = [
            "cve_id", "cvss_score", "severity", "affected_libraries",
            "library_path", "description",
            "created_at", "updated_at", "is_deleted"
        ]



class ImageSerializer(serializers.ModelSerializer):
    # 1) Nested, read-only display of full SecurityIssue objects
    security_issues = SecurityIssueSerializer(many=True, read_only=True)

    # 2) Write-only field to accept CVE IDs when posting/patching
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
        print("Received products_data in create:", products_payload)

        for pd in products_payload:
            pkg, created = Product.objects.get_or_create(
                name=pd['name'],
                defaults={
                    # Add other default fields here if needed, e.g.:
                    # 'description': pd.get('description', ''),
                    # 'status': 'active',
                }
            )
            patch.products.add(pkg)
            # Save helm_charts for the product if provided
            helm_charts_value = pd.get('helm_charts')
            if helm_charts_value is not None:
                PatchProductHelmChart.objects.update_or_create(
                    patch=patch,
                    product=pkg,
                    defaults={"helm_charts": helm_charts_value}
                )


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
                print("initial_products_data",initial_products_data)

        for pd_raw in initial_products_data:
            pkg = Product.objects.get(name=pd_raw['name'])
            product_security_des = pd_raw.get('product_security_des') 
            for img_dict in pd_raw.get('images', []):
                for issue in img_dict.get('security_issues', []):
                    cve_id = issue.get('cve_id')
                    # product_security_des = issue.get('product_security_des')

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
                # defaults={'version': jd.get('version')}
            )
            # update existing or create new PatchJar row
            PatchJar.objects.update_or_create(
                patch=patch,
                jar=jar_obj,
                defaults={'version': jd.get('version', None),
                'remarks': jd.get('remarks', '')}
            )

        # 5) Link scopes + remarks
        for sd in scopes_payload:
            scope_obj, _ = HighLevelScope.objects.get_or_create(
                name=sd['name'],
                # defaults={'version': sd.get('version')}
            )
            # update existing or create new through‐row
            PatchHighLevelScope.objects.update_or_create(
                patch=patch,
                scope=scope_obj,
                defaults={'version': sd.get('version', None),
                'remarks': sd.get('remarks', '')}
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
                pkg, created = Product.objects.get_or_create(
                    name=pd['name'],
                    defaults={
                        # Add other default fields here if needed
                    }
                )
                patch.products.add(pkg)
                # Update helm_charts if provided
                helm_charts_value = pd.get('helm_charts')
                if helm_charts_value is not None:
                    PatchProductHelmChart.objects.update_or_create(
                        patch=patch,
                        product=pkg,
                        defaults={"helm_charts": helm_charts_value}
                    )



                for img_dict in pd['images']:
                    img_name = img_dict.get('image_name')
                    # if not img_name:
                    #     raise serializers.ValidationError(f"Missing or empty 'image_name' for product '{pd['name']}'")

                    # ✅ Now img is only set if img_name is valid
                    existing_img = Image.objects.filter(image_name=img_name).first()

                    if existing_img and existing_img.build_number != patch.name:
                        # Create new image with new build_number
                        img, created = Image.objects.get_or_create(
                            product=pkg,
                            image_name=img_name,
                            build_number=patch.name,
                            defaults={
                                'is_deleted': False,
                                'release_date': patch.release_date 
                            }
                        )
                        img.twistlock_report_url = None
                        img.twistlock_report_clean = None
                        img.save()

                    elif existing_img and existing_img.build_number == patch.name:
                        # Use the existing one, update if needed
                        existing_img.is_deleted = False
                        existing_img.save()
                        img = existing_img

                    else:
                        # No existing image at all – ensure twistlock fields are null
                        img = Image.objects.create(
                            product=pkg,
                            image_name=img_name,
                            build_number=patch.name,
                            release_date= patch.release_date,
                            is_deleted=False,
                            twistlock_report_url=None,
                            twistlock_report_clean=None
                        )


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
                            'patch_build_number': img_dict.get('patch_build_number'),
                        }
                    )

        products_initial = self.initial_data.get('products_data', [])

        for pd_raw in products_initial:
            try:
                pkg = Product.objects.get(name=pd_raw['name'])
            except Product.DoesNotExist:
                continue  # or handle error
            product_security_des = pd_raw.get('product_security_des') 

            for img_dict in pd_raw.get('images', []):
                for issue in img_dict.get('security_issues', []):
                    cve_id = issue.get('cve_id')
                    # product_security_des = issue.get('product_security_des')

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
                    # defaults={'version': jd.get('version')}
                )
                PatchJar.objects.update_or_create(
                    patch=patch,
                    jar=jar_obj,
                    defaults={'version': jd.get('version', None),
                    'remarks': jd.get('remarks', '')}
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
                    # defaults={'version': sd.get('version')}
                )
                PatchHighLevelScope.objects.update_or_create(
                    patch=patch,
                    scope=scope_obj,
                    defaults={'version': sd.get('version', None),
                    'remarks': sd.get('remarks', '')}
                )

            # 2) Remove any old scopes not in the new payload
            kept = [ sd['name'] for sd in scopes_payload ]
            PatchHighLevelScope.objects.filter(
                patch=patch
            ).exclude(
                scope__name__in=kept
            ).delete()

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
