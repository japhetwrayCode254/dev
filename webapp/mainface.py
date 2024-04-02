

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
                person = Record.objects.get(id=ntnl_id)  # Retrieve the record with the matching ID
                
                # Construct the name using information from the matched record
                name = f"Name: {person.first_name}, National ID: {person.id}, Address: {person.address}"

                # Assuming you're trying to create an attendee record if the person is recognized
                attendee = RecordAdditionalInfo.objects.create(
                    name=person.first_name,
                    national_id=person.id,
                    address=person.address,
                    picture=person.images,
                    date_created=timezone.now().date(),
                    time_created=timezone.now().time(),
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
    return redirect('/week_page')



# detect faces using an image 
@login_required(login_url='my-login')
def detectImage(request):
    # This is an example of running face recognition on a single image
    # and drawing a box around each person that was identified.

    # Load a sample picture and learn how to recognize it.

    #upload image
    if request.method == 'POST' and request.FILES['image']:
        myfile = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        #person=Person.objects.create(name="Swimoz",user_id="1",address="2020 Nehosho",picture=uploaded_file_url[1:])
        #person.save()


    images=[]
    encodings=[]
    names=[]
    files=[]
    nationalIds = []

    prsn=Record.objects.all()
    for crime in prsn:
        images.append(crime.first_name+'_image')
        encodings.append(crime.first_name+'_face_encoding')
        files.append(crime.images)
        names.append(crime.first_name+ ' '+ crime.address)
        nationalIds.append(crime.id)


    for i in range(0,len(images)):
        images[i]=face_recognition.load_image_file(files[i])
        encodings[i]=face_recognition.face_encodings(images[i])[0]






    # Create arrays of known face encodings and their names
    known_face_encodings = encodings
    known_face_names = names
    n_id = nationalIds

    # Load an image with an unknown face
    unknown_image = face_recognition.load_image_file(uploaded_file_url[1:])

    # Find all the faces and face encodings in the unknown image
    face_locations = face_recognition.face_locations(unknown_image)
    face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

    # Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
    # See http://pillow.readthedocs.io/ for more about PIL/Pillow
    pil_image = Image.fromarray(unknown_image)
    # Create a Pillow ImageDraw Draw instance to draw with
    draw = ImageDraw.Draw(pil_image)

    # Loop through each face found in the unknown image
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        name = "Unknown"

        # If a match was found in known_face_encodings, just use the first one.
        # if True in matches:
        #     first_match_index = matches.index(True)
        #     name = known_face_names[first_match_index]

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if any(matches):
            best_match_index = matches.index(True)
            name = known_face_names[best_match_index]
            ntnl_id = n_id[best_match_index]
            
            # Retrieve information from the Record table based on the matched name
            try:
                matched_record = Record.objects.get(id=ntnl_id)
                current_time = timezone.now()
                # Create a new RecordAdditionalInfo object using information from the matched Record
                attendee = RecordAdditionalInfo.objects.create(
                    name=matched_record.first_name,
                    national_id=matched_record.id,
                    address=matched_record.address,
                    picture=matched_record.images,
                    date_created= datetime.datetime.now(),
                    time_created=datetime.datetime.utcnow(),
                    day_of_week = current_time.strftime("%A")
                )
                # Save the object
                attendee.save()
            except Record.DoesNotExist:
                pass  # Handle the case where the matched name is not found in the Record table



        # Draw a box around the face using the Pillow module
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

        # Draw a label with a name below the face
        text_width, text_height = draw.textsize(name)
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

    # Remove the drawing library from memory as per the Pillow docs
    del draw

    # Display the resulting image
    pil_image.show()
    return redirect('/today_page')

    # You can also save a copy of the new image to disk if you want by uncommenting this line
    # pil_image.save("image_with_boxes.jpg")