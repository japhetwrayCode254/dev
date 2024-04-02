from django.utils import timezone
import datetime
from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm, CreateRecordForm, UpdateRecordForm

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate

from django.contrib.auth.decorators import login_required

from .models import Record,RecordAdditionalInfo

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from PIL import Image, ImageDraw
import datetime
from django.core.paginator import Paginator


# modules 2

from django.http import StreamingHttpResponse
import cv2
import threading
import numpy as np
from PIL import Image
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder
from django.core.files.storage import default_storage
from django.conf import settings


# - Homepage 

def home(request):

    return render(request, 'webapp/index.html')


# - Register a user

def register(request):

    form = CreateUserForm()

    if request.method == "POST":

        form = CreateUserForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, "Account created successfully!")

            return redirect("my-login")

    context = {'form':form}

    return render(request, 'webapp/register.html', context=context)


# - Login a user

def my_login(request):

    form = LoginForm()

    if request.method == "POST":

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:

                auth.login(request, user)

                return redirect("face_page")

    context = {'form':form}

    return render(request, 'webapp/my-login.html', context=context)


# - Dashboard

@login_required(login_url='my-login')


def dashboard(request):
    # Retrieve all records
    my_records = Record.objects.all()
    
    # Pagination
    paginator = Paginator(my_records, 10)  # Change 10 to the desired number of records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'records': page_obj}
    
    return render(request, 'webapp/dashboard.html', context=context)



# - Create a record 

@login_required(login_url='my-login')
def create_record(request):

    form = CreateRecordForm()

    if request.method == "POST":

        form = CreateRecordForm(request.POST,request.FILES)

        if form.is_valid():

            form.save()

            messages.success(request, "Your record was created!")

            return redirect("dashboard")

    context = {'form': form}

    return render(request, 'webapp/create-record.html', context=context)


# - Update a record 

@login_required(login_url='my-login')
def update_record(request, pk):

    record = Record.objects.get(id=pk)

    form = UpdateRecordForm(instance=record)

    if request.method == 'POST':

        form = UpdateRecordForm(request.POST, instance=record)

        if form.is_valid():

            form.save()

            messages.success(request, "Your record was updated!")

            return redirect("dashboard")
        
    context = {'form':form}

    return render(request, 'webapp/update-record.html', context=context)


# - Read / View a singular record

@login_required(login_url='my-login')
def singular_record(request, pk):

    all_records = Record.objects.get(id=pk)

    context = {'record':all_records}

    return render(request, 'webapp/view-record.html', context=context)


# - Delete a record

@login_required(login_url='my-login')
def delete_record(request, pk):

    record = Record.objects.get(id=pk)

    record.delete()

    messages.success(request, "Your record was deleted!")

    return redirect("dashboard")



# - User logout

def user_logout(request):

    auth.logout(request)

    messages.success(request, "Logout success!")

    return redirect("my-login")


#  class  for detecting the face
@login_required(login_url='my-login')
def face_page(request):


    return render(request, 'webapp/face.html')






@login_required(login_url='my-login')
def today_page(request):
    # Retrieve all RecordAdditionalInfo objects
    records = RecordAdditionalInfo.objects.all()
    
    # Pagination
    paginator = Paginator(records, 10)  # Change 12 to the desired number of records per page
    page_number = request.GET.get('page')
    page_obje = paginator.get_page(page_number)
    
    # Pass records to the template for rendering
    return render(request, 'webapp/today.html', {'page_obje': page_obje})


@login_required(login_url='my-login')
def week_page(request):

    return render(request, 'webapp/week.html')

@login_required(login_url='my-login')
def stranger_page(request):
   
    return render(request, 'webapp/strangers.html')


# search data by using date


def search_by_date(request):
    if request.method == 'GET' and 'search_date' in request.GET:
        search_date = request.GET.get('search_date')
        records = RecordAdditionalInfo.objects.filter(date_created=search_date)
        
        # Pagination
        paginator = Paginator(records, 10)  # Change 10 to the desired number of records per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'webapp/logs.html', {'page_obj': page_obj})
    else:
        return render(request, 'webapp/logs.html')





#  face detect
@login_required(login_url='my-login')
def detectWithWebcam(request):
    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)

    # Load a sample picture and learn how to recognize it.
    images = []
    encodings = []
    names = []
    files = []
    nationalIds = []

    prsns = Record.objects.all()
    for record in prsns:
        images.append(record.first_name+'_image')
        encodings.append(record.first_name+'_face_encoding')
        files.append(record.images)
        names.append('Name: '+record.first_name+ ', National ID: '+ str(record.id)+', Address '+record.address)
        nationalIds.append(record.id)

    for i in range(0, len(images)):
        images[i] = face_recognition.load_image_file(files[i])
        encodings[i] = face_recognition.face_encodings(images[i])[0]

    # Create arrays of known face encodings and their names
    known_face_encodings = encodings
    known_face_names = names
    n_id = nationalIds
    identified_today = set()
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = frame[:, :, ::-1]

        # Find all the faces and face encodings in the frame of video
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Loop through each face in this frame of video
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

            name = "Unknown"

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                ntnl_id = n_id[best_match_index]
                person = Record.objects.get(id=ntnl_id)
                name = f"Name: {person.first_name}, National ID: {person.id}, Address: {person.address}"

                # Check if the person has been identified today and if a record with the same national ID and date already exists
                if person.id not in identified_today:
                    identified_today.add(person.id)

                    # Check if an attendee record with the same national ID and date already exists
                    existing_attendee = RecordAdditionalInfo.objects.filter(national_id=person.id, date_created=timezone.localdate()).exists()

                    if not existing_attendee:
                        # Create and save the attendee record
                        attendee = RecordAdditionalInfo.objects.create(
                            name=person.first_name,
                            national_id=person.id,
                            address=person.address,
                            picture=person.images,
                            date_created=timezone.localdate(),
                            time_created=timezone.localtime(),
                            day_of_week=timezone.now().strftime("%A")
                        )
                        attendee.save()

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Remove break condition to keep the loop running indefinitely
        # Hit 'q' on the keyboard to quit!
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

        # This will keep the loop running indefinitely until manually terminated
        if cv2.waitKey(1) == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
    return redirect('/today_page')


# detect faces using an image 
from django.db.models import Q
@login_required(login_url='my-login')

def detectImage(request):
    if request.method == 'POST' and request.FILES['image']:
        myfile = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        images = []
        encodings = []
        names = []
        files = []
        nationalIds = []

        prsn = Record.objects.all()
        for crime in prsn:
            images.append(crime.first_name + '_image')
            encodings.append(crime.first_name + '_face_encoding')
            files.append(crime.images)
            names.append(crime.first_name + ' ' + crime.address)
            nationalIds.append(crime.id)

        current_time = timezone.now().date()

        for i in range(len(images)):
            images[i] = face_recognition.load_image_file(files[i])
            encodings[i] = face_recognition.face_encodings(images[i])[0]

        known_face_encodings = encodings
        known_face_names = names
        n_id = nationalIds

        unknown_image = face_recognition.load_image_file(uploaded_file_url[1:])

        face_locations = face_recognition.face_locations(unknown_image)
        face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

        pil_image = Image.fromarray(unknown_image)
        draw = ImageDraw.Draw(pil_image)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if any(matches):
                best_match_index = matches.index(True)
                name = known_face_names[best_match_index]
                ntnl_id = n_id[best_match_index]

                existing_entry = RecordAdditionalInfo.objects.filter(
                    Q(national_id=ntnl_id) &
                    Q(date_created=current_time)
                ).exists()

                if not existing_entry:
                    try:
                        matched_record = Record.objects.get(id=ntnl_id)
                        attendee = RecordAdditionalInfo.objects.create(
                            name=matched_record.first_name,
                            national_id=matched_record.id,
                            address=matched_record.address,
                            picture=matched_record.images,
                            date_created=current_time,
                            time_created=datetime.datetime.now().time(),
                            day_of_week=current_time.strftime("%A")
                        )
                        attendee.save()
                    except Record.DoesNotExist:
                        pass

            draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
            text_width, text_height = draw.textsize(name)
            draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
            draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

        del draw

        pil_image.show()
        return redirect('/today_page')