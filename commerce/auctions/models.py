from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName = models.CharField(max_length = 50)
    
    def __str__(self):
        return self.categoryName
                                                    

class Bid(models.Model):
    bid = models.FloatField(default=0)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userbid")

                

class Listing(models.Model):
    title = models.CharField(max_length = 30)
    description = models.CharField(max_length = 305)
    imageUrl = models.CharField(max_length = 500)
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="itembid")
    status = models.BooleanField(default = True)
    owner = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True, related_name = "user")
    category = models.ForeignKey(Category, on_delete = models.CASCADE, blank = True, null = True, related_name = "category")
    watchlist = models.ManyToManyField(User, blank = True, null=True, related_name="userwatchlist")

    def __str__(self):
        return self.title 
    

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True, related_name = "usercomment")
    listing = models.ForeignKey(Listing, on_delete = models.CASCADE, blank = True, null = True, related_name = "listingcomment")
    message = models.CharField(max_length=250)

    def _str_(self):
        return f"{self.commenter} comment on {self.listing}" 
    
