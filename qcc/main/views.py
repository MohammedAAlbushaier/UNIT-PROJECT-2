import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.utils import timezone

from .models import Campaign, Donation, Accomplishment, UserProfile, CampaignImage
from .forms import (SignUpForm, UserProfileForm, UserUpdateForm,
                    CampaignForm, DonationForm, CampaignImageForm)
from django.contrib import messages
from django.db.models import Q

# Create your views here.




def index(request):
    active_campaigns = Campaign.objects.filter(is_active=True).order_by('-start_date')[:3]
    accomplishments = Accomplishment.objects.all().order_by('-date')[:5]
    return render(request, 'main/index.html', {
        'campaigns': active_campaigns,
        'accomplishments': accomplishments
    })


def about(request):
    return render(request, 'main/about.html')


def campaign_list(request):
    filter_type = request.GET.get('filter', 'active')
    if filter_type == 'active':
        campaigns = Campaign.objects.filter(is_active=True)
    elif filter_type == 'inactive':
        campaigns = Campaign.objects.filter(is_active=False)
    else:
        campaigns = Campaign.objects.all()

    return render(request, 'main/campaigns.html', {
        'campaigns': campaigns,
        'filter_type': filter_type
    })


def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    images = campaign.images.all()
    donations = campaign.donation_set.all().order_by('-donation_date')

    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.campaign = campaign
            if request.user.is_authenticated:
                donation.donor = request.user
            donation.save()

            # Update campaign current amount
            campaign.current_amount += donation.amount
            campaign.save()

            messages.success(request, 'Thank you for your donation!')
            return redirect('campaign_detail', pk=pk)
    else:
        form = DonationForm()

    return render(request, 'main/campaign_detail.html', {
        'campaign': campaign,
        'images': images,
        'donations': donations,
        'form': form
    })


@staff_member_required
def campaign_create(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.created_by = request.user
            campaign.save()

            # Handle multiple images
            images = request.FILES.getlist('images')
            for image in images:
                CampaignImage.objects.create(campaign=campaign, image=image)

            messages.success(request, 'Campaign created successfully!')
            return redirect('campaign_detail', pk=campaign.pk)
    else:
        form = CampaignForm()

    return render(request, 'main/campaign_form.html', {
        'form': form,
        'title': 'Create New Campaign'
    })


@staff_member_required
def campaign_update(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES, instance=campaign)
        if form.is_valid():
            form.save()

            # Handle additional images
            images = request.FILES.getlist('images')
            for image in images:
                CampaignImage.objects.create(campaign=campaign, image=image)

            messages.success(request, 'Campaign updated successfully!')
            return redirect('campaign_detail', pk=campaign.pk)
    else:
        form = CampaignForm(instance=campaign)

    return render(request, 'main/campaign_form.html', {
        'form': form,
        'title': 'Update Campaign',
        'campaign': campaign
    })


@staff_member_required
def campaign_delete(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == 'POST':
        campaign.delete()
        messages.success(request, 'Campaign deleted successfully!')
        return redirect('campaigns')

    return render(request, 'main/campaign_confirm_delete.html', {
        'campaign': campaign
    })


@login_required
def donate(request, pk=None):
    campaign = None
    if pk:
        campaign = get_object_or_404(Campaign, pk=pk)

    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            if request.user.is_authenticated:
                donation.donor = request.user
            if campaign:
                donation.campaign = campaign

            # Generate a transaction ID (in a real app, use your payment processor's ID)
            donation.transaction_id = f"QCC-{timezone.now().timestamp()}-{random.randint(1000, 9999)}"
            donation.save()

            # Update campaign amount if applicable
            if campaign:
                campaign.current_amount += donation.amount
                campaign.save()

            # Redirect to success page with transaction details
            return redirect(
                f"{reverse('payment_success')}?transaction_id={donation.transaction_id}&donation_id={donation.id}")
    else:
        form = DonationForm()

    return render(request, 'main/donate.html', {
        'form': form,
        'campaign': campaign
    })


def signup(request):
    if request.method == 'POST':
        user_form = SignUpForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()

            # Update the profile with additional fields
            profile = user.userprofile
            profile.phone_number = user_form.cleaned_data['phone_number']
            profile.street_name = user_form.cleaned_data['street_name']
            profile.city = user_form.cleaned_data['city']
            profile.country = user_form.cleaned_data['country']
            profile.postal_code = user_form.cleaned_data['postal_code']
            profile.preferred_contact = user_form.cleaned_data['preferred_contact']
            profile.save()

            messages.success(request, 'Account created successfully!')
            return redirect('signin')
    else:
        user_form = SignUpForm()

    return render(request, 'main/signup.html', {'form': user_form})


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)

    # Get user's donations and campaigns they've supported
    donations = Donation.objects.filter(donor=request.user).order_by('-donation_date')
    supported_campaigns = Campaign.objects.filter(
        donation__donor=request.user
    ).distinct()

    return render(request, 'main/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'donations': donations,
        'supported_campaigns': supported_campaigns
    })


def campaign_donate(request, pk):
    # Handle campaign-specific donations
    campaign = get_object_or_404(Campaign, pk=pk)
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.campaign = campaign
            if request.user.is_authenticated:
                donation.donor = request.user
            donation.save()

            # Update campaign current amount
            campaign.current_amount += donation.amount
            campaign.save()

            messages.success(request, 'Thank you for your donation!')
            return redirect('campaign_detail', pk=campaign.pk)
    else:
        form = DonationForm()

    return render(request, 'main/donate.html', {
        'form': form,
        'campaign': campaign
    })


def general_donate(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            if request.user.is_authenticated:
                donation.donor = request.user
            donation.save()
            messages.success(request, 'Thank you for your donation!')
            return redirect('index')
    else:
        form = DonationForm()

    return render(request, 'main/general_donate.html', {'form': form})


def payment_success(request):
    transaction_id = request.GET.get('transaction_id', '')
    donation_id = request.GET.get('donation_id', '')

    try:
        donation = Donation.objects.get(id=donation_id, transaction_id=transaction_id)
    except Donation.DoesNotExist:
        donation = None

    return render(request, 'main/payment_success.html', {
        'donation': donation
    })

