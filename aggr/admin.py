from django.contrib import admin

from .models import MediaPerson, UserProfile, Company, Critic, MediaItem, Music, Movie, Game, Console
from .models import CriticReview, UserReview
# Register your models here.

class UserProfileAdmin(admin.ModelAdmin):
    class Meta:
        model = UserProfile

class CriticReviewAdmin(admin.ModelAdmin):
    class Meta:
        model = CriticReview
		
class UserReviewAdmin(admin.ModelAdmin):
    class Meta:
        model = UserReview
		
class CriticAdmin(admin.ModelAdmin):
    class Meta:
        model = Critic
class PersonAdmin(admin.ModelAdmin):
    class Meta:
        model = MediaPerson

class ConsoleAdmin(admin.ModelAdmin):
    class Meta:
        model = Console
		
class CompanyAdmin(admin.ModelAdmin):
    class Meta:
        model = Company
		
class MediaItemAdmin(admin.ModelAdmin):
    class Meta:
        model = Music

class MusicAdmin(admin.ModelAdmin):
    class Meta:
        model = Music
		
class MovieAdmin(admin.ModelAdmin):
    class Meta:
        model = Movie
		
class GameAdmin(admin.ModelAdmin):
    class Meta:
        model = Game
		
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(MediaItem, MediaItemAdmin)
admin.site.register(Critic, CriticAdmin)
admin.site.register(CriticReview, CriticReviewAdmin)
admin.site.register(UserReview, UserReviewAdmin)
admin.site.register(MediaPerson, PersonAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Console, ConsoleAdmin)
admin.site.register(Music, MusicAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Game, GameAdmin)