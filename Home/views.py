from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
import datetime
from dbfire.users import *
from datetime import timedelta, datetime, timezone
from django.db.models import Q


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['pass']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Bad Credentials!")
            return redirect('signin')

    return render(request, "signin.html")


def signout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('signin')


def index(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('signin')


def home(request):
    """
    Dashboard View. Consists summary statics of App
    """
    if request.user.is_authenticated:
        # Getting All Users
        total_users, all_users = get_all_users()

        # Num of Users with Instagram Account
        users_with_insta = len(get_social_users(('instagram',)))

        # Num of Users without Instagram Account
        non_insta_users = total_users - users_with_insta

        # Num of Users with Twitter Account
        users_with_twitter = len(get_social_users(('twitter',)))

        # Num of Users without Twitter Account
        non_twitter_users = total_users - users_with_twitter

        # Users with insta or twitter accounts
        users_with_twitter_or_insta = len(get_social_users(('instagram', 'twitter')))

        # Users with insta only accounts, no twitter
        users_with_insta_only = len(get_social_users(('instagram',), True))

        # Users with twitter only accounts, no insta
        users_with_twitter_only = len(get_social_users(('twitter',), True))

        # Users without any Social Account
        non_social_users = len(get_social_users(tuple()))

        # Users in past 6 months
        month_start = datetime.today().replace(day=1).strftime("%Y-%m-%d").split('-')
        month_start = datetime(*list(map(int, month_start)),
                          tzinfo=timezone.utc)
        months_ago = {}
        for i in range(7):
            month_ago_date = (month_start - timedelta(days=430+30*(6-i)))
            month_ago_month = month_ago_date.strftime('%B-%y')
            month_ago_date = month_ago_date.strftime("%Y-%m-%dT%H:%M:%S%z")
            month_ago_date = month_ago_date[:-2] + ":" + month_ago_date[-2:]
            months_ago[month_ago_month] = len(get_filtered_users({'time_created': (month_ago_date, 'lte')}))

        # Top 5 Users with highest number of followers
        users_by_followers = get_filtered_users({},limit = 5, order = 'desc', limit_by='num_followers')

        # Users joined through referrals
        direct_users = len(get_filtered_users({'invited_by_user_profile': ('null', 'eq')}))
        referred_users = total_users - direct_users

        # Num of Users joined since a specified date
        time_since = datetime(2020, 5, 1, 0, 0, 0, 0,
                                       tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
        time_since = time_since[:-2] + ":" + time_since[-2:]
        time_since_str = datetime(2020, 5, 1, 0, 0, 0, 0, tzinfo=timezone.utc).strftime("%m-%d-%y")
        num_users_since = len(get_filtered_users({'time_created': (time_since, 'gte')}))

        # List of variables to send to Render
        context = {
            "total_users": total_users,
            "non_insta_users": non_insta_users,
            "users_with_insta": users_with_insta,
            "non_twitter_users": non_twitter_users,
            "users_with_twitter": users_with_twitter,
            "num_users_since": num_users_since,
            "time_since": time_since_str,
            "direct_users": direct_users,
            "referred_users": referred_users,
            "non_social_users": non_social_users,
            "months_ago": months_ago,
            "users_by_followers": users_by_followers,
            # "twitter_insta_users": users_with_twitter_or_insta,
            # "users_insta_only": users_with_insta_only,
            # "users_twitter_only": users_with_twitter_only
        }
        return render(request, "Home.html", context=context)
    else:
        return redirect('signin')


def user_admin(request):
    """
    User Admin View. User statistics, user search etc.
    """
    if request.user.is_authenticated:
        search_keyword = request.GET.get('q')
        user = None
        if search_keyword:
            if search_keyword.isdigit():
                search_keyword = int(search_keyword)
            else:
                search_keyword = search_keyword.lower()
            get_funcs = [get_user_by_id, get_users_by_name, get_user_by_insta, get_user_by_twitter, get_user_by_username]
            for func in get_funcs:
                user = func(search_keyword)
                if user:
                    break
                else:
                    continue
        if not user:
            return render(request, 'users_admin.html', context={})
        else:
            if isinstance(user, list):
                for u in user:
                    u.time_created = datetime.strptime(u.time_created[:-3] + u.time_created[-2:], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d %B %Y")
            else:
                user.time_created = datetime.strptime(user.time_created[:-3] + user.time_created[-2:], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d %B %Y")
            return render(request, 'users_admin.html', context={'users': user if isinstance(user, list) else [user]})
    else:
        return redirect('signin')

