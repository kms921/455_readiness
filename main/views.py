import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Attribute, InputData, AttributeType
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import bcrypt
# Create your views here.
# one parameter named request

def remove_duplicates(a_list):
    new_list = []
    for item in a_list:
        if item not in new_list:
            new_list.append(item)
    return new_list

# Test for date
# Helper function to add flags to the attributes
def add_flag():
    flags = Attribute.objects.exclude(attribute_type__in = AttributeType.objects.filter(alert_type = 'None'))
    for flag in flags:
        if flag.attribute_type.alert_type == 'fail' and flag.value == "F":
            flag.alert_or_warning = "alert"
        elif flag.attribute_type.alert_type == 'yes_is_bad' and flag.value == 'Y':
            flag.alert_or_warning = "alert"
        elif flag.attribute_type.alert_type == 'no_is_bad' and flag.value == 'N':
            flag.alert_or_warning = "alert"
        elif flag.attribute_type.alert_type == 'Dateback':
            if len(flag.value) >= 6:
                if len(flag.value) == 8 and '-' not in flag.value and '/' not in flag.value:
                    date_time_obj = datetime.strptime(flag.value, '%Y%m%d')
                else:
                    date_time_obj = datetime.strptime(flag.value, '%Y-%m-%d')
                date_time_obj = date_time_obj.date()
            today = date.today()
            a_year_ago = today + relativedelta(years=-1)
            nine_months_ago = today + relativedelta(months = -9)
            if date_time_obj <= a_year_ago:
                flag.alert_or_warning = 'alert'
            elif date_time_obj <= nine_months_ago:
                flag.alert_or_warning = 'warning'
        elif flag.attribute_type.alert_type == 'Dateforward':
            if len(flag.value) >= 6:
                if len(flag.value) == 8 and '-' not in flag.value and '/' not in flag.value:
                    date_time_obj = datetime.strptime(flag.value, '%Y%m%d')
                else:
                    date_time_obj = datetime.strptime(flag.value, '%Y-%m-%d')
                date_time_obj = date_time_obj.date()
                today = date.today()
                a_year_from_now = today + relativedelta(years=1)
                nine_months_from_now = today + relativedelta(months=9)
                if date_time_obj <= nine_months_from_now:
                    flag.alert_or_warning = 'alert'
                elif date_time_obj <= a_year_from_now:
                    flag.alert_or_warning = 'warning'
        else:
            flag.alert_or_warning = None
        flag.save()
    return None

def profile_upload(request):
    hashed = bcrypt.hashpw('password'.encode(), bcrypt.gensalt()).decode()
    # declaring template
    template = "add_csv.html"
    data = User.objects.all()
# prompt is a context variable that can have different values      depending on their context
    prompt = {
        'order': 'Order of the CSV should be name, email, address,    phone, profile',
        'profiles': data
    }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')


    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)
    # print(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        _, created = User.objects.update_or_create(
            last_name=column[0],
            first_name=column[1],
            middle_initial=column[2],
            rank=column[3],
            military_email=column[4],
            password= hashed,
            leadership_type=column[5],
            hq=1,
            platoon=column[7],
            squad=column[8],
            team=column[9],
            active=True,
        )
    return redirect('/dashboard')

def index(request):
    return render(request, 'index.html')

def logout(request):
    request.session.clear()
    request.session.flush()
    return redirect('/')

def login(request):
    errors = User.objects.login_validator(request.POST)
    if len(errors) > 0:
        for message in errors.values():
            messages.error(request, message)
        return redirect('/')
    users = User.objects.filter(military_email=request.POST['military_email'])
    if users: #because users is a list here it will return a boolian if the list is empty or not
        logging_in_user = users[0]
        if bcrypt.checkpw(request.POST['password'].encode(), logging_in_user.password.encode()):
            request.session['user_id'] = logging_in_user.id
            return redirect('/dashboard')
        else:
            messages.error(request, "Incorrect Password")
    else:
        messages.error(request, "Email not found")
    return redirect('/')

def add_user(request):
    errors = User.objects.registration_validator(request.POST)
    if len(errors) > 0:
        for message in errors.values():
            messages.error(request, message)
        return redirect('/dashboard')
    hashed = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
    new_user = User.objects.create(
        last_name = request.POST['last_name'],
        first_name = request.POST['first_name'],
        middle_initial = request.POST['middle'],
        rank = request.POST['rank'],
        military_email = request.POST['military_email'],
        password = hashed,
        leadership_type = request.POST['leadership'],
        hq = 1,
        platoon = request.POST['platoon'],
        squad = request.POST['squad'],
        team = request.POST['team'],
        active = request.POST['active'],
    )
    return redirect('/dashboard')

def register(request):
    errors = User.objects.registration_validator(request.POST)
    if len(errors) > 0:
        for message in errors.values():
            messages.error(request, message)
        return redirect('/')
    hashed = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
    new_user = User.objects.create(
        last_name = request.POST['last_name'],
        first_name = request.POST['first_name'],
        middle_initial = request.POST['middle'],
        rank = request.POST['rank'],
        military_email = request.POST['military_email'],
        password = hashed,
        leadership_type = request.POST['leadership'],
        hq = 1,
        platoon = request.POST['platoon'],
        squad = request.POST['squad'],
        team = request.POST['team'],
        active = request.POST['active'],
    )
    request.session['user_id'] = new_user.id
    return redirect('/dashboard')

def dashboard(request):
    if not request.session.get('user_id', None):
        return redirect('/')
    this_soldier = User.objects.get(id = request.session['user_id'])
    if this_soldier.leadership_type == 'none':
        these_soldiers = this_soldier
    elif this_soldier.leadership_type == "team":
        these_soldiers = User.objects.filter(platoon = this_soldier.platoon).filter(squad = this_soldier.squad).filter(team = this_soldier.team)
    elif this_soldier.leadership_type == "squad":
        these_soldiers = User.objects.filter(platoon = this_soldier.platoon).filter(squad = this_soldier.squad)
    elif this_soldier.leadership_type == "platoon" or this_soldier.leadership_type == "Platoon Sergeant":
        these_soldiers = User.objects.filter(platoon = this_soldier.platoon).exclude(leadership_type = 'admin')
    elif this_soldier.leadership_type == "admin":
        these_soldiers = User.objects.all().order_by('last_name')
    all_attributes = AttributeType.objects.all().order_by('type')
    add_flag()
    # list_of_attributes = []
    if all_attributes:
        pass
        # for key in all_attributes:
            # list_of_attributes.append(key.type)
        # list_of_attributes = remove_duplicates(list_of_attributes)
    if this_soldier == these_soldiers:
        list_of_flags = Attribute.objects.filter(alert_or_warning__in=['alert', 'warning'], user = this_soldier)
    else:
        list_of_flags = Attribute.objects.filter(alert_or_warning__in=['alert', 'warning'], user__in=these_soldiers)
    context = {
        'all_soldiers': User.objects.all(),
        'this_soldier': this_soldier,
        'these_soldiers': these_soldiers,
        'all_attributes': all_attributes,
        'list_of_flags': list_of_flags,
    }
    return render(request, 'Soldier_Tracker.html', context)

def add_info(request):
    users = User.objects.filter(id = request.session['user_id'])
    if users:
        user = users[0]
    if len(InputData.objects.filter(user = user)) > 0:
        data_to_update = InputData.objects.get(user = user)
        if len(request.POST['location']) > 0:
            data_to_update.location = request.POST['location']
        if len(request.POST['phone_number']) > 0:
            data_to_update.phone_number = request.POST['phone_number']
        if len(request.POST['address']) > 0:
            data_to_update.address = request.POST['address']
        if len(request.POST['city']) > 0:
            data_to_update.city = request.POST['city']
        if len(request.POST['state']) > 0:
            data_to_update.state = request.POST['state']
        if len(request.POST['zipcode']) > 0:
            data_to_update.zipcode = request.POST['zipcode']
        if len(request.POST['civilian_email']) > 0:
            data_to_update.civilian_email = request.POST['civilian_email']
        if len(request.POST['unit_origin']) > 0:
            data_to_update.unit_origin = request.POST['unit_origin']
        if len(request.POST['unit_destination']) > 0:
            data_to_update.unit_destination = request.POST['unit_destination']
        if len(request.POST['plans_after']) > 0:
            data_to_update.plans_after = request.POST['plans_after']
        if len(request.POST['military_schools']) > 0:
            data_to_update.military_school = request.POST['military_schools']
        if len(request.POST['civilian_school']) > 0:
            data_to_update.civilian_school = request.POST['civilian_school']
        if len(request.POST['credits']) > 0:
            data_to_update.num_credits = request.POST['credits']
        if len(request.POST['major']) > 0:
            data_to_update.major = request.POST['major']
        if len(request.POST['employer']) > 0:
            data_to_update.employer = request.POST['employer']
        data_to_update.save()
        return redirect('/dashboard')
    else:
        errors = InputData.objects.form_validator(request.POST)
        if len(errors) > 0:
            for message in errors.values():
                messages.error(request, message)
            return redirect('/dashboard')
        InputData.objects.create(
            location = request.POST['location'],
            phone_number = request.POST['phone_number'],
            address = request.POST['address'],
            city = request.POST['city'],
            state = request.POST['state'],
            zipcode = request.POST['zipcode'],
            civilian_email = request.POST['civilian_email'],
            unit_origin = request.POST['unit_origin'],
            unit_destination = request.POST['unit_destination'],
            plans_after = request.POST['plans_after'],
            military_schools = request.POST['military_schools'],
            civilian_school = request.POST['civilian_school'],
            num_credits = request.POST['credits'],
            major = request.POST['major'],
            employer = request.POST['employer'],
            user = user,
        )
        return redirect('/dashboard')

def changePassword(request):
    hashed = bcrypt.hashpw('password'.encode(), bcrypt.gensalt()).decode()
    users = User.objects.filter(id = request.POST['military_email'])
    if users:
        user = users[0]
        print(user.last_name)
        user.password = hashed
        user.save()
        return redirect('/dashboard')

def deactivate(request):
    user = User.objects.get(id = request.POST['military_email'])
    user.active = request.POST['deactivate']
    user.save()
    return redirect('/dashboard')

def reactivate(request):
    user = User.objects.get(id = request.POST['military_email'])
    user.active = request.POST['reactivate']
    user.save()
    return redirect('/dashboard')

def add_attributes(request):
    for key, value in request.POST.items():
        user = User.objects.get(id = request.POST['military_email'])
        all_attribute_types = AttributeType.objects.all()
        list_of_attributes = []
    for item in all_attribute_types:
        list_of_attributes.append(item.type)
    list_of_attributes = remove_duplicates(list_of_attributes)
    for key, value in request.POST.items():
        if value and key not in ["csrfmiddlewaretoken", "military_email"]:
            try:
                attribute = Attribute.objects.get(name = key, user = user)
                attribute.value = value
                attribute.save()
            except Attribute.DoesNotExist:
                try:
                    attributetype = AttributeType.objects.get(type = key)
                except AttributeType.DoesNotExist:
                    attributetype = AttributeType.objects.create(
                        type = key,
                        alert_type = None
                    )
                Attribute.objects.create(
                    name = key, 
                    value = value,
                    attribute_type = attributetype,
                    user = user
                )
    return redirect('/dashboard')
    
def user_change_password(request):
    errors = User.objects.password_reset_validator(request.POST)
    if len(errors) > 0:
        for message in errors.values():
            messages.error(request, message)
            return redirect('/')
    user = User.objects.get(id = request.session['user_id'])
    if bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
        hashed = bcrypt.hashpw(request.POST['new_password'].encode(), bcrypt.gensalt()).decode()
        user.password=hashed
        user.save()
        print("user.password")
        return redirect('/dashboard')
    messages.error(request, "Incorrect Password")
    

def add_alerts_warnings(request):
    # print("made it here.")
    for key, value in request.POST.items():
        # print(key, value, "Key and value from adding alerts.")
        if key not in ["csrfmiddlewaretoken", "military_email"]:
            try:
                this_attribute_type = AttributeType.objects.get(type = key)
                errors = AttributeType.objects.alerts_validator(this_attribute_type, value)
                if len(errors) > 0:
                    for message in errors.values():
                        messages.error(request, message)
                        return redirect('/dashboard')
                this_attribute_type.alert_type = value
            except AttributeType.DoesNotExist:
                this_attribute_type = AttributeType.objects.create(type = key)
                this_attribute_type.alert_type = value
            this_attribute_type.save()
    return redirect('/dashboard')

def display_name(request):
    attribute = AttributeType.objects.get(id = request.POST['attribute'])
    attribute.display_name = request.POST['display_name']
    attribute.save()
    return redirect('/dashboard')

def delete_attribute(request):
    if request.POST['soldier_to_remove_attribute_for'] == '0':
        object_to_delete = AttributeType.objects.get(id = request.POST['attribute_to_delete'])
        object_to_delete.delete()
        return redirect('/dashboard')
    else:
        user = User.objects.get(id = request.POST['soldier_to_remove_attribute_for'])
        attribute_to_delete = Attribute.objects.get(attribute_type = request.POST['attribute_to_delete'], user = user)
        attribute_to_delete.delete()
    return redirect('/dashboard')

def attribute_upload(request):
    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    row1 = next(io_string)
    headers = row1.split(',')
    # print(headers)
    for row in csv.reader(io_string, delimiter=',', quotechar='|'):
        counter = 0
        # users = User.objects.filter(military_email = row[0].strip())
        # user = users[0]
        for column in row:
            users = User.objects.filter(military_email = row[0].strip())
            user = users[0]
            # print(user.first_name)
            # print('Header:',headers[counter].strip())
            # print('Value', column.strip())
            if len(column.strip()) != 0:
                if len(AttributeType.objects.filter(type = headers[counter].strip())) > 0:
                    a_type = AttributeType.objects.get(type = headers[counter].strip())
                else:
                    a_type = AttributeType.objects.create(type = headers[counter].strip())
                # try:
                #     a_type = AttributeType.objects.get(type = headers[counter].strip())
                # except AttributeType.DoesNotExist:
                #     a_type = AttributeType.objects.create(type = headers[counter].strip())
                if len(Attribute.objects.filter(name = headers[counter].strip(), user = user)) > 0:
                    attribute_to_update = Attribute.objects.get(name = headers[counter].strip(), user = user)
                    attribute_to_update.value = column.strip()
                    attribute_to_update.attribute_type = a_type
                    attribute_to_update.user = user
                    attribute_to_update.save()
                else:
                    Attribute.objects.create(
                        name = headers[counter].strip(),
                        value = column.strip(),
                        attribute_type = a_type,
                        user = user,
                    )
                # try:
                #     attribute_to_update = Attribute.objects.get(name = headers[counter].strip())
                #     attribute_to_update.value = column.strip()
                #     attribute_to_update.attribute_type = a_type
                #     attribute_to_update.user = user
                #     attribute_to_update.save()
                # except Attribute.DoesNotExist:
                #     Attribute.objects.create(
                #         name = headers[counter].strip(),
                #         value = column.strip(),
                #         attribute_type = a_type,
                #         user = user,
                #     )
            counter += 1
    # for user in User.objects.all():
        # for attribute in user.attributes.all():
            # print(attribute.name, attribute.value)
    return redirect('/dashboard')

def new_attribute (request):
    if len(AttributeType.objects.filter(type= request.POST['new_attribute_name'])) == 0:
        new_attribute= AttributeType.objects.create(type = request.POST['new_attribute_name'])
        if request.POST['soldier_to_add_attribute_to'] == '0':
            for soldier in User.objects.filter(active = True):
                Attribute.objects.create(name=request.POST['new_attribute_name'],user=soldier, attribute_type=new_attribute, value=request.POST['value'])
        else:
            user = User.objects.get(id = request.POST['soldier_to_add_attribute_to'])
            Attribute.objects.create(name=request.POST['new_attribute_name'],user=user, attribute_type=new_attribute, value=request.POST['value'])
    else: 
        this = AttributeType.objects.get(type= request.POST['new_attribute_name'])
        if request.POST['soldier_to_add_attribute_to'] == '0':
            for soldier in User.objects.filter(active = True):
                if len(Attribute.objects.filter(id= this.id, user=soldier)) > 0:
                    this_attribute= Attribute.objects.get(id = this, user=soldier)
                    this_attribute.value=request.POST['value']
                    this_attribute.save()
                else: 
                    Attribute.objects.create(name=request.POST['new_attribute_name'], user=soldier, attribute_type=this, value=request.POST['value'])
        else: 
            user = User.objects.get(id = request.POST['soldier_to_add_attribute_to'])
            if len(Attribute.objects.filter(id = this.id, user=user)) > 0:
                    this_attribute= Attribute.objects.get(id = this, user=user)
                    this_attribute.value=request.POST['value']
                    this_attribute.save()
            else: 
                Attribute.objects.create(name=request.POST['new_attribute_name'], user=user, attribute_type=this, value=request.POST['value'])
    return redirect('/dashboard')
