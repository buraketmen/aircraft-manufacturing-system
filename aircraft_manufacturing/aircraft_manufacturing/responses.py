from rest_framework import serializers

class GeneralSuccessResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)

    class Meta:
        fields = ("detail",)

class GeneralFailedResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)

    class Meta:
        fields = ("detail", "code",)