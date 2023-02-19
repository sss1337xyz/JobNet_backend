from rest_framework import serializers

from kwork.models import Services, Deals


class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = [
            'user',
            'title',
            'image',
            'description',
            'price',
            'requirements',
            'slug'
        ]


class DealsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deals
        fields = [
            'seller',
            'buyer',
            'description',
            'price',
            'status',
            'days_on_deal',
            'date_start_deal',
            'date_create',
            'date_finish'
        ]

    @staticmethod
    def validate_user1_not_user2(user1, user2):
        if user1 == user2:
            raise serializers.ValidationError({'status': 5001, 'detail': 'Seller and Buyer must be different users.'})
        return True

    def create(self, validated_data):
        seller = validated_data.get('seller')
        buyer = validated_data.get('buyer')

        # Проверяем, что seller и buyer не являются одним и тем же пользователем
        self.validate_user1_not_user2(seller, buyer)

        deal = Deals.objects.create(**validated_data)
        return deal
