
from rest_framework import serializers
from .models import Release, Patch, Product, Image, Jar, HighLevelScope, SecurityIssue, PatchJar, PatchHighLevelScope, PatchProductImage,PatchImage

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
class SecurityIssueWithProductDescriptionSerializer(serializers.ModelSerializer):
    product_security_des = serializers.SerializerMethodField()

    class Meta:
        model = SecurityIssue
        fields = [
            'cve_id',
            'cvss_score',
            'severity',
            'affected_libraries',
            'library_path',
            'description',
            'product_security_des',
            'created_at',
            'updated_at',
            'is_deleted'
        ]

    def get_product_security_des(self, obj):
        product = self.context.get('product')
        if not product:
            return None
        link = ProductSecurityIssue.objects.filter(product=product, security_issue=obj).first()
        return link.product_security_des if link else None

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
            'security_issues', 'security_issue_ids'   # read nested
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

    def get_security_issues(self, obj):
        product = self.context.get('product')  # passed from outer serializer
        security_issues = obj.security_issues.filter(is_deleted=False)
        return SecurityIssueWithProductDescriptionSerializer(
            security_issues,
            many=True,
            context={'product': product}
        ).data


class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

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
    ot2_pass = serializers.CharField()
    registry = serializers.CharField()
    helm_charts = serializers.CharField()
    patch_build_number = serializers.CharField()

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
        products_list = []

        for product in obj.products.filter(is_deleted=False):
            imgs = Image.objects.filter(
                product=product,
                patchproductimage__patch=obj,
                is_deleted=False
            ).distinct()

            images_data = []

            for img in imgs:
                # Serialize basic image data
                image_serialized = ImageSerializer(img).data

                # Attach patch-specific fields from PatchImage
                try:
                    patch_image = PatchImage.objects.get(patch=obj, image=img)
                    image_serialized.update({
                        "ot2_pass": patch_image.ot2_pass,
                        "registry": patch_image.registry,
                        "helm_charts": patch_image.helm_charts,
                        "patch_build_number": patch_image.patch_build_number,
                    })
                except PatchImage.DoesNotExist:
                    pass

                # Inject product-specific security field into each security issue
                for issue in image_serialized.get("security_issues", []):
                    issue["product_security_des"] = self.get_product_security_description(product, issue)

                images_data.append(image_serialized)

            products_list.append({
                "name": product.name,
                "images": images_data,
            })

        return products_list

    def get_product_security_description(self, product, issue):
        # Customize this if you want to query DB or use logic
        return f"Explanation specific to {product.name} for {issue.get('cve_id')}"
