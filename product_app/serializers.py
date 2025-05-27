
from rest_framework import serializers
from .models import Release, Patch, Product, Image, Jar, HighLevelScope, SecurityIssue, PatchJar, PatchHighLevelScope, PatchProductImage

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
            'ot2_pass', 'twistlock_report_url', 'twistlock_report_clean',
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

class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

class PatchJarSerializer(serializers.ModelSerializer):
    name    = serializers.CharField(source='jar.name', read_only=True)
    version = serializers.CharField(source='jar.version', read_only=True)
    remarks = serializers.CharField()

    class Meta:
        model  = PatchJar
        fields = ('name', 'version', 'remarks')

class PatchHighLevelScopeSerializer(serializers.ModelSerializer):
    name    = serializers.CharField(source='scope.name', read_only=True)
    version = serializers.CharField(source='scope.version', read_only=True)
    remarks = serializers.CharField()

    class Meta:
        model  = PatchHighLevelScope
        fields = ('name', 'version', 'remarks')

# class PatchSerializer(serializers.ModelSerializer):
#     # third_party_jars = JarSerializer(many=True, read_only=True)
#     # high_level_scope = HighLevelScopeSerializer(many=True, read_only=True)
#     jars   = PatchJarSerializer(
#                  source='patchjar_set', many=True, read_only=True
#              )
#     scopes = PatchHighLevelScopeSerializer(
#                  source='patchhighlevelscope_set', many=True, read_only=True
#              )

#     jars_data   = serializers.ListField(child=serializers.DictField(), write_only=True)
#     scopes_data = serializers.ListField(child=serializers.DictField(), write_only=True)
#     # class Meta:
#     #     model = Patch
#     #     exclude = ('products', 'images')  # Don't show directly
#     #     # fields = '__all__'
#     # 1️⃣ write‐only: what the client POSTs/PATCHes
#     products_data = serializers.ListField(
#         child=serializers.DictField(), 
#         write_only=True
#     )

#     # 2️⃣ read‐only: what you return on GET
#     products = serializers.SerializerMethodField()

#     class Meta:
#         model   = Patch
#         # switch from exclude to explicit so you can include products_data + products
#         fields  = [
#             'name', 'release', 'release_date', 'kick_off', 'code_freeze',
#             'platform_qa_build', 'client_build_availability',
#             'description', 'patch_state',
#             'jars', 'scopes',      # your existing through-model read fields
#             'products_data',       # ✍️ write-only
#             'products',            # 👁 read-only nested
#         ]
#         extra_kwargs = {
#             'products_data': {'required': True},
#         }

#     def create(self, validated_data):
#         products_payload = validated_data.pop('products_data')
#         patch = super().create(validated_data)

#         for pd in products_payload:
#             pkg = Product.objects.get(name=pd['name'])
#             patch.products.add(pkg)
#             for img in pd['images']:
#                 img_obj = Image.objects.get(image_name=img, product=pkg)
#                 PatchProductImage.objects.create(
#                     patch=patch, product=pkg, image=img_obj
#                 )
#         return patch

#     def update(self, instance, validated_data):
#         payload = validated_data.pop('products_data', None)
#         patch = super().update(instance, validated_data)

#         if payload is not None:
#             # clear out old links
#             PatchProductImage.objects.filter(patch=patch).delete()
#             patch.products.clear()

#             for pd in payload:
#                 pkg = Product.objects.get(name=pd['name'])
#                 patch.products.add(pkg)
#                 for img in pd['images']:
#                     img_obj = Image.objects.get(image_name=img, product=pkg)
#                     PatchProductImage.objects.create(
#                         patch=patch, product=pkg, image=img_obj
#                     )
#         return patch

#     def get_products(self, obj):
#         """
#         Builds the nested structure for GET / PATCH/:id
#         """
#         out = []
#         for pkg in obj.products.filter(is_deleted=False):
#             images = Image.objects.filter(
#                 product=pkg,
#                 patchproductimage__patch=obj,
#                 is_deleted=False
#             )
#             out.append({
#                 'name': pkg.name,
#                 'images': ImageSerializer(images, many=True).data
#             })
#         return out

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
    products_data = serializers.ListField(
                        child=serializers.DictField(), write_only=True
                    )

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

        # 3) Link products & images
        for pd in products_payload:
            pkg = Product.objects.get(name=pd['name'])
            patch.products.add(pkg)
            for img_name in pd['images']:
                img = Image.objects.get(image_name=img_name, product=pkg)
                PatchProductImage.objects.create(
                    patch=patch, product=pkg, image=img
                )

        # 4) Link jars + remarks
        # for jd in jars_payload:
        #     jar_obj, _ = Jar.objects.get_or_create(
        #         name=jd['name'],
        #         defaults={'version': jd.get('version')}
        #     )
        #     patch.third_party_jars.add(jar_obj)
        #     PatchJar.objects.create(
        #         patch=patch,
        #         jar=jar_obj,
        #         remarks=jd.get('remarks', '')
        #     )
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

        # 2) Update the Patch fields
        patch = super().update(instance, validated_data)

        # 3) If products_data sent, clear & re-create
        if products_payload is not None:
            PatchProductImage.objects.filter(patch=patch).delete()
            patch.products.clear()
            for pd in products_payload:
                pkg = Product.objects.get(name=pd['name'])
                patch.products.add(pkg)
                for img_name in pd['images']:
                    img = Image.objects.get(image_name=img_name, product=pkg)
                    PatchProductImage.objects.create(
                        patch=patch, product=pkg, image=img
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

    def get_products(self, obj):
        """
        Build the nested products → images structure for reads.
        """
        out = []
        for pkg in obj.products.filter(is_deleted=False):
            imgs = Image.objects.filter(
                product=pkg,
                patchproductimage__patch=obj,
                is_deleted=False
            )
            out.append({
                'name': pkg.name,
                'images': ImageSerializer(imgs, many=True).data
            })
        return out