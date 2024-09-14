from django.shortcuts import render
from django.shortcuts import render, HttpResponse, get_object_or_404
from .forms import MyLoginForm, UserRegistrationForm
from django.contrib.auth import logout
from .models import Plan, Payment, Author
from django.contrib.auth import authenticate, login


# Create your views here.

def main(request):
    return render(request, 'mainpage.html')


def userhomepage(request):
    return render(request, 'userhomepage.html')


from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse


def user_login(request):
    if request.method == 'POST':
        login_form = MyLoginForm(request.POST)
        if login_form.is_valid():
            cleaned_data = login_form.cleaned_data
            auth_user = authenticate(request, username=cleaned_data['username'], password=cleaned_data['password'])

            if auth_user is not None:
                login(request, auth_user)

                # Redirect based on the username
                if auth_user.username == 'admin':  # Admin login
                    return redirect('home_path')  # Change 'adminpage' to your admin page URL name
                else:
                    return redirect('userhomepage')  # Change 'userhomepage' to your user homepage URL name

            else:
                return HttpResponse('Not Authenticated')
    else:
        login_form = MyLoginForm()

    return render(request, 'useraccount/login_form.html', {'login_form': login_form})


def register(request):
    if request.method == 'POST':
        user_reg_form = UserRegistrationForm(request.POST)
        if user_reg_form.is_valid():
            new_user = user_reg_form.save(commit=False)
            new_user.set_password(user_reg_form.cleaned_data['password1'])
            new_user.save()
            return render(request, 'account/register_done.html', {'user_reg_form': user_reg_form})
    else:
        user_reg_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_reg_form': user_reg_form})


def user_logout_view(request):
    logout(request)
    return redirect('main')


def subscription_list(request):
    subscription_list = Plan.objects.all()
    print(subscription_list)
    return render(request, 'useraccount/subscription.html', {'subscription_list': subscription_list})


from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from django.utils import timezone
from .models import Plan, Subscription, Payment, Book, Feedback, Rental, RentalList, Genre
from .forms import BookSearchForm, FeedbackForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal


def select_plan(request):
    # Check if the user has an active subscription
    active_subscription = Subscription.objects.filter(
        user=request.user,
        end_date__gt=timezone.now()
    ).first()

    if active_subscription:
        # User already has a plan, show message
        return render(request, 'useraccount/existing_plan.html', {
            'active_subscription': active_subscription,
            'message': 'You already have an active subscription!'
        })

    # If no active plan, show available subscription plans
    plans = Plan.objects.all()

    if request.method == 'POST':
        selected_plan_id = request.POST.get('plan')
        selected_plan = get_object_or_404(Plan, id=selected_plan_id)

        # Redirect to payment page
        return redirect('process_payment', plan_id=selected_plan.id)

    return render(request, 'useraccount/subscription.html', {'plans': plans})


def process_payment(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    user = request.user

    # Check if the user has an active subscription
    active_subscription = Subscription.objects.filter(
        user=user,
        end_date__gt=timezone.now()  # Active subscription if current time is before end_date
    ).first()

    if active_subscription:
        # Redirect to the existing_plan page if the user has an active subscription
        return render(request, 'useraccount/existing_plan.html', {
            'active_subscription': active_subscription,
            'message': 'You already have an active subscription! You cannot select a new plan until your current one expires.'
        })

    if request.method == 'POST':
        # Handle form submission
        mode_of_payment = request.POST.get('mode_of_payment')

        # Create a new payment record with the selected payment mode
        Payment.objects.create(
            user=user,
            plan=plan,
            cost=plan.cost,
            payment_for='Subscription',
            mode_of_payment=mode_of_payment,
            date_and_time=timezone.now()  # Set to the current time
        )

        # Set the duration manually without using `relativedelta`
        duration = plan.details.split()
        time_value = int(duration[0])
        time_unit = duration[1].lower()

        if time_unit == 'days':
            end_date = timezone.now() + timedelta(days=time_value)
        elif time_unit == 'weeks':
            end_date = timezone.now() + timedelta(weeks=time_value)
        elif time_unit == 'months':
            end_date = timezone.now() + timedelta(days=time_value * 30)  # Approximation for months
        elif time_unit in ['year', 'years']:
            end_date = timezone.now() + timedelta(days=time_value * 365)  # Approximation for years
        else:
            end_date = timezone.now()

        # Create a new subscription for the user
        Subscription.objects.create(
            user=user,
            plan=plan,
            start_date=timezone.now(),
            end_date=end_date
        )

        # Redirect to the payment success page
        return redirect('payment_success')

    return render(request, 'useraccount/process_payment.html', {'plan': plan})


def existing_plan(request):
    active_subscription = Subscription.objects.filter(
        user=request.user,
        end_date__gt=timezone.now()
    ).first()

    if not active_subscription:
        # If no active plan, redirect them to the available plans page
        return redirect('plans')

    return render(request, 'useraccount/existing_plan.html', {
        'active_subscription': active_subscription
    })


def payment_success(request):
    return render(request, 'useraccount/payment_success.html')


def list_of_books(request):
    form = BookSearchForm(request.GET)
    books = Book.objects.all()

    if form.is_valid():
        title = form.cleaned_data.get('title')
        author = form.cleaned_data.get('author')
        genre = form.cleaned_data.get('genre')

        if title:
            books = books.filter(title__icontains=title)
        if author:
            books = books.filter(author__icontains=author)
        if genre:
            books = books.filter(genre__icontains=genre)

    context = {
        'books': books,
        'form': form,
    }
    return render(request, 'useraccount/list_of_books.html', context)


def book_details(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Check if there is an active rental for the user and this book
    rental = Rental.objects.filter(user=request.user, book=book, rental_status='rented').first()

    # Create a new rental if it doesn't exist
    if not rental:
        rental_start = timezone.now()
        rental_end = rental_start + timedelta(days=7)  # 7-day rental period

        # Create the Rental object and set rent_amount from the book's price
        rental = Rental.objects.create(
            user=request.user,
            book=book,
            rental_start_date=rental_start,
            rental_end_date=rental_end,
            rent_amount=book.price  # Set the rent_amount from the book's price
        )

    return render(request, 'useraccount/book_details.html', {
        'book': book,
        'rental': rental,
    })


def list_of_authors(request):
    authors = Author.objects.all()
    return render(request, 'list_of_author.html', {'authors': authors})


def author_details(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    return render(request, 'author_details.html', {'author': author})


@login_required
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            return redirect('feedback_success')  # Redirect to a success page
    else:
        form = FeedbackForm()

    # Fetch the user's feedback to display
    user_feedback = Feedback.objects.filter(user=request.user)

    return render(request, 'feedback.html', {'form': form, 'user_feedback': user_feedback})


def feedback_success(request):
    return render(request, 'feedback_success.html')


def rental_payment(request, rental_id):
    # Fetch rental object by its unique id
    rental = get_object_or_404(Rental, id=rental_id)
    book = rental.book

    # Define tax rate
    tax_rate = Decimal('0.18')  # 18% tax rate

    if request.method == 'POST':
        payment_mode = request.POST.get('mode_of_payment')

        # Calculate tax and total amount
        tax_amount = rental.rent_amount * tax_rate
        total_amount = rental.rent_amount + tax_amount

        # Handle the payment processing logic here
        # For now, we assume the payment is always successful

        # Update the rental with payment information
        rental.payment_mode = payment_mode
        rental.payment_date = timezone.now()

        # Save the rental instance with updated payment information
        rental.save()

        # Redirect to the payment success page
        return redirect('payment_success')

    # Calculate amounts for GET request
    tax_amount = rental.rent_amount * tax_rate
    total_amount = rental.rent_amount + tax_amount

    return render(request, 'rental_payment.html', {
        'rental': rental,
        'book': book,
        'tax_amount': tax_amount,
        'total_amount': total_amount
    })


@login_required  # Ensures the user must be logged in
def rental_list(request):
    print("im here")
    user = request.user  # Get the current logged-in user
    rentals = Rental.objects.filter(user=user)  # Filter rentals by the logged-in user

    if request.method == 'POST':
        rental_id = request.POST.get('rental_id')  # Get the rental ID to update the correct rental
        payment_mode = request.POST.get('mode_of_payment')
        print(payment_mode);
        tax_rate = 0.18  # Example tax rate, define this properly or fetch from settings

        # Get the rental object
        try:
            rental = Rental.objects.get(id=rental_id, user=user)  # Ensure we get the user's rental
        except Rental.DoesNotExist:
            # Handle the case where the rental is not found
            return render(request, 'rental_list.html', {'rentals': rentals, 'error': 'Rental not found'})

        # Calculate tax and total amount
        tax_amount = rental.rent_amount * tax_rate
        total_amount = rental.rent_amount + tax_amount

        # Handle payment processing logic here (assumed successful for now)

        # Update the rental with payment information
        rental.payment_mode = payment_mode
        rental.payment_date = timezone.now()
        rental.save()

    return render(request, 'rental_list.html', {'rentals': rentals})


def copy_rental_to_rentallist(rental_id):
    try:
        rental = Rental.objects.get(id=rental_id)
        # Copy relevant fields from Rental to RentalList
        new_rentallist = RentalList(
            user=rental.user,  # Assuming you have a user field in RentalList
            book=rental.book,  # Assuming a book field exists in both models
            rent_amount=rental.rent_amount,
            start_date=rental.start_date,
            end_date=rental.end_date,
            # Add other fields as needed
        )
        new_rentallist.save()  # Save the copied data to RentalList
    except Rental.DoesNotExist:
        print("Rental does not exist")


def user_homepage(request):
    # Your logic to get user-specific data if needed
    return render(request, 'userhomepage.html')


def genre_list(request):
    genres = Genre.objects.all()  # Fetch all genres
    return render(request, 'genre_list.html', {'genres': genres})


@login_required
def user_profile(request):
    user = request.user  # This gets the currently logged-in user
    return render(request, 'profile.html', {'user': user})