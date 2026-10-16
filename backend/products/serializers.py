from rest_framework import serializers

from .models import Product


class ProductSerializer(
    serializers.ModelSerializer
):

    image_url = serializers.SerializerMethodField()

    class Meta:

        model = Product

        fields = (
            "id",
            "name",
            "description",
            "reference_price",
            "image",
            "image_url",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def get_image_url(
        self,
        obj,
    ):

        if not obj.image:
            return None

        request = self.context.get(
            "request"
        )

        if request:
            return request.build_absolute_uri(
                obj.image.url
            )

        return obj.image.url