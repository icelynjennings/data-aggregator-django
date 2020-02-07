from rest_framework import serializers

from .models import MediaItem

class MediaItemSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = MediaItem
		fields = ('author','name','score','user_score','genres','hits')