from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid


def index(request):
    activeListings = Listing.objects.filter(status = True)
    allcategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": allcategories

    })

def addBid(request, id):
    newBid = request.POST['newBid']
    listinginfo = Listing.objects.get(pk=id)
    listinginwatchlist = request.user in listinginfo.watchlist.all()
    allComments = Comment.objects.filter(listing=listinginfo)
    if int(newBid) > listinginfo.price.bid:
        updatedbid = Bid(bidder=request.user, bid=int(newBid))
        updatedbid.save()
        listinginfo.price = updatedbid
        listinginfo.save()
        return render(request, "auctions/listing.html", {
            "listing": listinginfo,
            "message": "bid has been placed",
            "update": True,
            "listinginwatchlist" : listinginwatchlist,
            "allComments" : allComments
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listinginfo,
            "message": "place a higher bid",
            "update": False,
            "listinginwatchlist" : listinginwatchlist,
            "allComments" : allComments
        })

def addComment(request, id):
    currentUser = request.user
    listinginfo = Listing.objects.get(pk=id)
    message = request.POST['newComment']

    newComment = Comment(
        commenter=currentUser,
        listing=listinginfo,
        message=message

    )

    newComment.save()

    return HttpResponseRedirect(reverse("listing", args=(id, )))

def categoryselection(request):
    if request.method=="POST":
        fcategory = request.POST['category']
        scategory = Category.objects.get(categoryName = fcategory)
        activeListings = Listing.objects.filter(status = True, category= scategory)
        allcategories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": activeListings,
            "categories": allcategories

    })

def removeWatchlist(request, id):
    listinginfo = Listing.objects.get(pk=id)
    currentUser = request.user
    listinginfo.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def userwatchlist(request):
    currentUser = request.user
    listings = Listing.objects.filter(watchlist=currentUser)
    return render(request, "auctions/watchlist.html", {
        "listings":listings
    })

def addWatchlist(request, id):
    listinginfo = Listing.objects.get(pk=id)
    currentUser = request.user
    listinginfo.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def listing(request, id):
    listinginfo = Listing.objects.get(pk=id)
    listinginwatchlist = request.user in listinginfo.watchlist.all()
    allComments = Comment.objects.filter(listing=listinginfo)
    isOwner = request.user.username == listinginfo.owner.username
    return render(request, "auctions/listing.html" ,{
        "listing": listinginfo,
        "listinginwatchlist" : listinginwatchlist,
        "allComments" : allComments,
        "isOwner": isOwner,
        "update": True,
        
    })

def closeAuction(request, id):
    listinginfo = Listing.objects.get(pk=id)
    listinginfo.status = False
    listinginfo.save()
    isOwner = request.user.username == listinginfo.owner.username
    listinginwatchlist = request.user in listinginfo.watchlist.all()
    allComments = Comment.objects.filter(listing=listinginfo)
    return render(request, "auctions/listing.html", {
         "listing": listinginfo,
        "listinginwatchlist" : listinginwatchlist,
        "allComments" : allComments,
        "isOwner": isOwner,
        "message": "your item was sold to the highest bidder"
    })


def createlisting(request):
    if request.method == "GET":
        allcategories = Category.objects.all()
        return render(request, "auctions/create.html" , {
            "categories": allcategories
        })
    else:
        title = request.POST["title"]
        description = request.POST["description"]
        imageURL = request.POST["imgurl"]
        price = request.POST["price"]
        category = request.POST["category"]
        seller = request.user
        bid = Bid(bid=float(price), bidder = seller)
        bid.save()
        categoryData = Category.objects.get(categoryName = category)

        newlisting = Listing(
            title = title,
            description = description,
            imageUrl = imageURL,
            price = bid,
            category = categoryData,
            owner = seller
        )
        newlisting.save()
        return HttpResponseRedirect(reverse(index))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
