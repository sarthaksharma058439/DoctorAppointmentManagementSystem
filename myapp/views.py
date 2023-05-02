from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.conf import settings
import pickle
from reportlab.pdfgen import canvas
import os
from pathlib import Path
import pathlib
from PIL import Image
import os, os.path
import glob
import base64
from random import randint
import smtplib
from email.mime.multipart import MIMEMultipart
import razorpay
from email.mime.text import MIMEText

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest



BASE_DIR = Path(__file__).resolve().parent.parent
app_logo = "logo.png"

def admindashboard(request):
    all_doctors_list = []
    all_patient_list = []

    registered_doctor_dict = {}
    registered_patient_dict = {}

    try:
        pickle_in_doctor = open("doctors.pickle", "rb")
        pickledata_doctor = pickle.load(pickle_in_doctor)
        registered_doctor_dict = pickledata_doctor.get("registereddoctors")
    except:
        pass
    
    for i in pickledata_doctor.get("registereddoctors"):
        all_doctors_list.append(i)
    ##

    try:
        pickle_in_patient = open("patients.pickle", "rb")
        pickledata_patient = pickle.load(pickle_in_patient)
        registered_patient_dict = pickledata_patient.get("registeredpatients")
    except:
        pass
    
    for i in pickledata_patient.get("registeredpatients"):
        all_patient_list.append(i)

    ##

    if request.method == "POST":
        approvalFor = request.POST.get("group1")
        approvalEmail = request.POST.get("approvalemail")

        if approvalFor == "approvedoctor":
            if approvalEmail in all_doctors_list:
                if (registered_doctor_dict.get(approvalEmail)["verified"]) == "0":
                    registered_doctor_dict.get(approvalEmail)["verified"] = "1"
                    
                    pickle_out = open("doctors.pickle", "wb")
                    pickledata = {'registereddoctors': registered_doctor_dict}
                    pickle.dump(pickledata, pickle_out)
                    pickle_out.close()     

                    return render(request, "admindashboard.html", {"mymessage":"Account approved.","Flag":"True"})               
                else:
                    return render(request, "admindashboard.html", {"mymessage":"This account is already approved.","Flag":"True"})
            else:
                return render(request, "admindashboard.html", {"mymessage":"Please create your account first.","Flag":"True"})
        else:
            if approvalEmail in all_patient_list:
                if (registered_patient_dict.get(approvalEmail)["verified"]) == "0":
                    registered_patient_dict.get(approvalEmail)["verified"] = "1"
                    
                    pickle_out = open("patients.pickle", "wb")
                    pickledata = {'registeredpatients': registered_patient_dict}
                    pickle.dump(pickledata, pickle_out)
                    pickle_out.close()     

                    return render(request, "admindashboard.html", {"mymessage":"Account approved.","Flag":"True"})               
                else:
                    print(registered_patient_dict)
                    return render(request, "admindashboard.html", {"mymessage":"This account is already approved.","Flag":"True"})
            else:
                return render(request, "admindashboard.html", {"mymessage":"Please create your account first.","Flag":"True"})

        # print(approvalFor)
        # print(approvalEmail)

        

    return render(request,'admindashboard.html')

def adminpanel(request):
    if request.method == "POST":
        adminusername = request.POST.get("adminusername")
        adminpassword = request.POST.get("adminpassword")

        if adminusername == "admin":
            if adminpassword == "admin":
                return redirect("admindashboard")
            else:
                return render(request,"adminpanel.html",{"mymessage":"Please check your your password.","Flag":"True"})

    return render(request,"adminpanel.html")

def blogs(request):
    return render(request, 'blogs.html')

def blog1(request):
    return render(request, 'blog1.html')

def blog2(request):
    return render(request, 'blog2.html')

def blog3(request):
    return render(request, 'blog3.html')

def blog4(request):
    return render(request, 'blog4.html')

def blog5(request):
    return render(request, 'blog5.html')

def videocall(request):
    return render(request,'videocall.html')

# def videocall_p(request):
#     return render(request,'videocall.html')

def index(request):
    return render(request, "index.html")

def home(request):
    return render(request, "home.html")

def about(request):
    return render(request, "about.html")

def doctors(request):
    return render(request, "doctors.html")

def departments(request):
    return render(request, "departments.html")

def doctorlogin(request):

    registereddoctors = {}

    if request.method == 'POST':

        doctorusername = request.POST.get('doctorusername')
        doctorpassword = request.POST.get('doctorpassword')

        try:
            pickle_in = open("doctors.pickle", "rb")
            pickledata = pickle.load(pickle_in)
            registereddoctors = pickledata.get('registereddoctors')
            print(registereddoctors)
        except:
            pass

       
        #print(doctorusername)
        #print(doctorpassword)

        canDoctorLogin = False


        if len(registereddoctors)>0:
            for i in registereddoctors:
                #print(i)
                print(registereddoctors.get(i).get("password"))

                if i == doctorusername and registereddoctors.get(i).get("password") == doctorpassword:
                    if registereddoctors.get(i).get("verified") == "0":
                        return render(request,"doctorlogin.html",{"mymessage":"Please ask admin for account approval.","Flag":"True"})
                    else:

                        print("Login Succesful.")
                        request.session["doctorusername"] = doctorusername

                        canDoctorLogin = True
                        break
                else:
                    print("please check your password")

            if canDoctorLogin:
                return redirect('doctordashboard')
            else:
                print("please create account first.")

        else:
            print("please create account first")

    return render(request, "doctorlogin.html")

def doctorverification(request):

    BASE_DIR = Path(__file__).resolve().parent.parent
    
    registereddoctors = {}
    sent_otp = request.session["doctor_otp"]
    doctor_otp_entry = request.POST.get("doctor_otp_entry")
    print(type(sent_otp))
    print(type(doctor_otp_entry))
    if request.method == "POST":
        if str(sent_otp) != str(doctor_otp_entry):
            return render(request, "doctorverification.html", {"mymessage":"Please check your otp.","Flag":"True"})
        else:
            newdoctorusername = request.session["verifydoctor_username"]
            newdoctorpassword = request.session["verifydoctor_password"]
            newdoctorconfirmpassword = request.session["verifydoctor_confirmpassword"]
            newdoctorage = request.session["verifydoctor_age"]
            newdoctorqualification = request.session["verifydoctor_qualification"]
            newdoctordepartment = request.session["verifydoctor_department"]
            newdoctorexperience = request.session["verifydoctor_Experience"]
            newdoctorphone = request.session["verifydoctor_phone"]
            newdoctoraadhaar = request.session["verifydoctor_aadhaar"]
            newdoctorpan = request.session["verifydoctor_pan"]

            try:
                pickle_in = open("tempdata.pickle", "rb")
                pickledata = pickle.load(pickle_in)
                doctorprofilepic = pickledata.get('verifydoctor_pic')
            except:
                pass

            #doctorprofilepic = request.session["verifydoctor_pic"]
            

            file_name = "{}{}.jpg".format(os.path.join(BASE_DIR, 'myapp/static/myapp/'),newdoctorusername)
            print(file_name)    
            try:
                pickle_in = open("doctors.pickle", "rb")
                pickledata = pickle.load(pickle_in)
                registereddoctors = pickledata.get('registereddoctors')
            except:
                pass

            canCreateNewDoctor = True
            if len(registereddoctors)>0:
                for i in registereddoctors:
                    if i == newdoctorusername:
                        print("doctor with this username already exist.")
                        canCreateNewDoctor = False
                #time_slots = {"slot1": "10 am to 11 am", "slot2": "11 am to 12 am",
            #"slot3": "1 pm to 2 pm", "slot4": "5 pm to 6 pm", "slot5": "6 pm to 7 pm", "slot6": "7 pm to 8 pm"}
            booked = []
            if canCreateNewDoctor:
                registereddoctors[newdoctorusername] = {"username":newdoctorusername, "password":newdoctorpassword, "booked_slots":[],
                "age":newdoctorage,
                "qualification":newdoctorqualification,
                "department":newdoctordepartment,
                "experience":newdoctorexperience,
                "phone":newdoctorphone,
                "aadhaar":newdoctoraadhaar,
                "pan":newdoctorpan,
                "verified":"0"}

            request.session["doctorusername"] = newdoctorusername
                    
                #print(registereddoctors)

            pickle_out = open("doctors.pickle", "wb")
            pickledata = {'registereddoctors': registereddoctors}
            pickle.dump(pickledata, pickle_out)
            pickle_out.close()
            with open(file_name,'wb') as f:
                f.write(doctorprofilepic)

            return render(request,"doctorverification.html",{"mymessage":"Account Created.","Flag":"True"})

    return render(request, "doctorverification.html")

def doctorsignup(request):

    BASE_DIR = Path(__file__).resolve().parent.parent
    
    registereddoctors = {}

    if request.method == 'POST':

        newdoctorusername = request.POST.get('newdoctorusername')
        newdoctorpassword = request.POST.get('newdoctorpassword')
        newdoctorconfirmpassword = request.POST.get('newdoctorconfirmpassword')
        newdoctorage = request.POST.get("doctorage")
        newdoctorqualification = request.POST.get("doctorqualification")
        newdoctordepartment = request.POST.get("doctordepartment")
        newdoctorexperience = request.POST.get("doctorexperience")
        newdoctorphone = request.POST.get("doctorphone")
        newdoctoraadhaar = request.POST.get("doctoraadhaar")
        newdoctorpan = request.POST.get("doctorpan")

        doctorprofilepic = request.FILES['my_uploaded_pic'].read()

        request.session["verifydoctor_username"] = newdoctorusername
        request.session["verifydoctor_password"] = newdoctorpassword
        request.session["verifydoctor_confirmpassword"] = newdoctorconfirmpassword
        request.session["verifydoctor_age"] = newdoctorage
        request.session["verifydoctor_qualification"] = newdoctorqualification
        request.session["verifydoctor_department"] = newdoctordepartment
        request.session["verifydoctor_Experience"] = newdoctorexperience
        request.session["verifydoctor_phone"] = newdoctorphone
        request.session["verifydoctor_aadhaar"] = newdoctoraadhaar
        request.session["verifydoctor_pan"] = newdoctorpan


        pickle_out = open("tempdata.pickle", "wb")
        pickledata = {'verifydoctor_pic': doctorprofilepic}
        pickle.dump(pickledata, pickle_out)
        pickle_out.close()

        #request.session["verifydoctor_pic"] = doctorprofilepic
        #generate otp
        otp = randint(100000, 999999)
        msg = MIMEMultipart()
        msg['From'] = 'shrmsarthak2661@gmail.com'
        msg['To'] = newdoctorusername
        msg['Subject'] = "Verification Code | MEDWAY HEALTHCARE"
        message = "Your 6 digit OTP is : "+str(otp)
        msg.attach(MIMEText(message))

        mailserver = smtplib.SMTP('smtp.gmail.com',587)
        # identify ourselves to smtp gmail client
        mailserver.ehlo()
        # secure our email with tls encryption
        mailserver.starttls()
        # re-identify ourselves as an encrypted connection
        mailserver.ehlo()
        mailserver.login('shrmsarthak2661@gmail.com', 'yqxgjmuprpcoirbf')

        mailserver.sendmail('shrmsarthak2661@gmail.com',newdoctorusername,msg.as_string())

        mailserver.quit()

        request.session["doctor_otp"] = otp

        return redirect('doctorverification')

    return render(request, "doctorsignup.html")

def patientlogin(request):
    
    registeredpatients = {}

    if request.method == 'POST':

        patientusername = request.POST.get('patientusername')
        patientpassword = request.POST.get('patientpassword')

        try:
            pickle_in = open("patients.pickle", "rb")
            pickledata = pickle.load(pickle_in)
            registeredpatients = pickledata.get('registeredpatients')
            print(registeredpatients)
        except:
            pass

       

        canPatientLogin = False

        #print(registeredpatients)
        #print(patientpassword)

        if len(registeredpatients)>0:
            for i in registeredpatients:
                #print(i)
                #print(registeredpatients.get(i).get("password"))
                if i == patientusername and registeredpatients.get(i).get("password") == patientpassword:
                    if registeredpatients.get(i).get("verified") == "0":
                        return render(request,"patientlogin.html",{"mymessage":"Please ask admin for account approval.","Flag":"True"})
                    else:
                        print("Login Succesful.")
                        canPatientLogin = True
                        request.session["username"] = patientusername
                        break
                else:
                    print("please check your password")

            if canPatientLogin:
                return redirect('patientdashboard')
            else:
                print("please create account first.")

        else:
            print("please create account first")

    return render(request, "patientlogin.html")

def ratedoctor(request):

    doctor_rate_dict = {}
    current_patient_nn = request.session["username"]

    if request.method == "POST":
        rate_doctor_username = request.POST.get("rate_doctor_username")
        doctor_rating = request.POST.get("doctor_rating")
        print("doctor_rating"+str(doctor_rating))
        doctor_rate_dict[rate_doctor_username] = {"patient_name":current_patient_nn,
        "rating":doctor_rating}

        pickle_out = open("ratedoctor.pickle", "wb")
        pickledata = {'doctor_rate_dict': doctor_rate_dict}
        pickle.dump(pickledata, pickle_out)
        pickle_out.close()

        print(doctor_rate_dict)

        return render(request,"ratedoctor.html",{"mymessage":"Rating Submitted.","Flag":"True"})

    return render(request, "ratedoctor.html")
def reportdoctor(request):

    doctor_report_dict = {}
    current_patient_n = request.session["username"]

    if request.method == "POST":
        report_doctor_username = request.POST.get("report_doctor_username")
        report_doctor_message = request.POST.get("report_doctor_message")

        doctor_report_dict[report_doctor_username] = {"patient_name":current_patient_n,
        "report_message":report_doctor_message}

        pickle_out = open("reportdoctor.pickle", "wb")
        pickledata = {'doctor_report_dict': doctor_report_dict}
        pickle.dump(pickledata, pickle_out)
        pickle_out.close()

        print(doctor_report_dict)

        return render(request,"reportdoctor.html",{"mymessage":"Report Submitted.","Flag":"True"})

    return render(request, "reportdoctor.html")

def patientverification(request):
    
    BASE_DIR = Path(__file__).resolve().parent.parent

    registeredpatients = {}
    sent_otp = request.session["patient_otp"]
    patient_otp_entry = request.POST.get("patient_otp_entry")
    print(type(sent_otp))
    print(type(patient_otp_entry))

    if request.method == "POST":
        if str(sent_otp) != str(patient_otp_entry):
            return render(request, "patientverification.html", {"mymessage":"Please check your otp.","Flag":"True"})
        else:

            newpatientusername = request.session["verifypatient_username"]
            newpatientpassword = request.session["verifypatient_password"]
            newpatientconfirmpassword = request.session["verifypatient_confirmpassword"]
            newpatientage = request.session["verifypatient_age"]
            newpatientphone = request.session["verifypatient_phone"]
            newpatientaadhaar = request.session["verifypatient_aadhaar"]
            newpatientpan = request.session["verifypatient_pan"]

            try:
                pickle_in = open("tempdata.pickle", "rb")
                pickledata = pickle.load(pickle_in)
                patientprofilepic = pickledata.get('verifypatient_pic')
            except:
                pass

            file_name = "{}{}.jpg".format(os.path.join(BASE_DIR, 'myapp/static/myapp/'),newpatientusername)

            try:
                pickle_in = open("patients.pickle", "rb")
                pickledata = pickle.load(pickle_in)
                registeredpatients = pickledata.get('registeredpatients')
            except:
                pass

            canCreateNewPatient = True
            if len(registeredpatients)>0:
                for i in registeredpatients:
                    if i == newpatientusername:
                        print("patient with this username already exist.")
                        canCreateNewPatient = False

            if canCreateNewPatient:

                registeredpatients[newpatientusername] = {"username":newpatientusername, "password":newpatientpassword,
                "age":newpatientage,
                "phone":newpatientphone,
                "aadhaar":newpatientaadhaar,
                "pan":newpatientpan,
                "verified":"0"}

                print(registeredpatients)

                pickle_out = open("patients.pickle", "wb")
                pickledata = {'registeredpatients': registeredpatients}
                pickle.dump(pickledata, pickle_out)
                pickle_out.close()

                with open(file_name,'wb') as f:
                    f.write(patientprofilepic)


                request.session["username"] = newpatientusername

                return render(request,"patientverification.html",{"mymessage":"Account Created.","Flag":"True"})

    return render(request,"patientverification.html")

def patientsignup(request):
    registeredpatients = {}

    if request.method == 'POST':

        newpatientusername = request.POST.get('newpatientusername')
        newpatientpassword = request.POST.get('newpatientpassword')
        newpatientconfirmpassword = request.POST.get('newpatientconfirmpassword')
        newpatientage = request.POST.get('patientage')
        newpatientphone = request.POST.get('patientphone')
        newpatientaadhaar = request.POST.get('patientaadhaar')
        newpatientpan = request.POST.get('patientpan')
        
        patientprofilepic = request.FILES['patient_pic'].read()

        ###
        request.session["verifypatient_username"] = newpatientusername
        request.session["verifypatient_password"] = newpatientpassword
        request.session["verifypatient_confirmpassword"] = newpatientconfirmpassword
        request.session["verifypatient_age"] = newpatientage
        request.session["verifypatient_phone"] = newpatientphone
        request.session["verifypatient_aadhaar"] = newpatientaadhaar
        request.session["verifypatient_pan"] = newpatientpan


        pickle_out = open("tempdata.pickle", "wb")
        pickledata = {'verifypatient_pic': patientprofilepic}
        pickle.dump(pickledata, pickle_out)
        pickle_out.close()

        #request.session["verifydoctor_pic"] = doctorprofilepic
        #generate otp
        otp = randint(100000, 999999)
        msg = MIMEMultipart()
        msg['From'] = 'shrmsarthak2661@gmail.com'
        msg['To'] = newpatientusername
        msg['Subject'] = "Verification Code | MEDWAY HEALTHCARE"
        message = "Your 6 digit OTP is : "+str(otp)
        msg.attach(MIMEText(message))

        mailserver = smtplib.SMTP('smtp.gmail.com',587)
        # identify ourselves to smtp gmail client
        mailserver.ehlo()
        # secure our email with tls encryption
        mailserver.starttls()
        # re-identify ourselves as an encrypted connection
        mailserver.ehlo()
        mailserver.login('shrmsarthak2661@gmail.com', 'yqxgjmuprpcoirbf')

        mailserver.sendmail('shrmsarthak2661@gmail.com',newpatientusername,msg.as_string())

        mailserver.quit()

        request.session["patient_otp"] = otp

        return redirect('patientverification')

        ###





    return render(request, "patientsignup.html")

def createpatientreport(request):
    doctorusername = request.session["doctorusername"]
    if request.method == "POST":

        pickledata_report = {}
        registered_patients = []



        try:
            pickle_in = open("patients.pickle", "rb")
            pickledata = pickle.load(pickle_in)
            
            for i in pickledata.get('registeredpatients'):
                registered_patients.append(i.split("@")[0])

            print(registered_patients)

        except:
            pass

        try:
            pickle_in_report = open("patientreports.pickle", "rb")
            pickledata_report = pickle.load(pickle_in_report)

            print(pickledata_report)
        except:
            pass

        

        patient_username = request.POST.get('patient_username')
        patient_prescription = request.POST.get('patient_prescription')
        
        pickledata_report[patient_username] = patient_prescription + ":"+ doctorusername 

        if patient_username not in registered_patients:
            return render(request, "createpatientreportPage.html",context = {"mymessage":"Please enter correct username.","Flag":"True"}) 
        else:
            pickle_out = open("patientreports.pickle", "wb")
            #pickledata_report = {'prescriptions': patient_prescription_dict}
            pickle.dump(pickledata_report, pickle_out)
            pickle_out.close()

            return render(request, "createpatientreportPage.html",context = {"mymessage":"Report generated for patient : "+patient_username,"Flag":"True"})

        print(patient_username)
        print(patient_prescription)
        
    return render(request, 'createpatientreportPage.html')

def doctorpersonaldetails(request):
    try:
        pickle_in = open("doctors.pickle", "rb")
        pickledata = pickle.load(pickle_in)
        registereddoctors = pickledata.get('registereddoctors')
        print(registereddoctors)

        
    except:
        pass

    current_doctor = request.session["doctorusername"]

    doctor_email = registereddoctors.get(current_doctor)["username"]
    doctor_age = registereddoctors.get(current_doctor)["age"]
    doctor_qualification = registereddoctors.get(current_doctor)["qualification"]
    doctor_department = registereddoctors.get(current_doctor)["department"]
    doctor_experience = registereddoctors.get(current_doctor)["experience"]
    doctor_phone = registereddoctors.get(current_doctor)["phone"]
    doctor_aadhaar = registereddoctors.get(current_doctor)["aadhaar"]
    doctor_pan = registereddoctors.get(current_doctor)["pan"]
    doctor_pic = file_name = "{}{}.jpg".format(os.path.join(BASE_DIR, 'myapp/static/'),doctor_email)
    print(doctor_pic)

    return render(request, "doctorpersonaldetails.html",{"doctor_email":doctor_email,
        "doctor_age":doctor_age,
        "doctor_qualification":doctor_qualification,
        "doctor_department":doctor_department,
        "doctor_experience":doctor_experience,
        "doctor_phone":doctor_phone,
        "doctor_aadhaar":doctor_aadhaar,
        "doctor_pan":doctor_pan,
        "doctor_pic":doctor_pic})

def doctordashboard(request):

    if 'logout2' in request.POST:
        return redirect('/')

    if 'callpatient' in request.POST:
        return redirect('/videocall')

    if 'createpatientreport' in request.POST:
        return redirect('/createpatientreport')

    if 'personaldetails' in request.POST:
        return redirect('/doctorpersonaldetails')


    d_name_list = []
    d_age_list = []
    d_address_list = []
    d_date_list = []
    d_time_list = []
    d_message_list = []
    d_status_list = []

    bookingdata = {}

    
    #print(username)
    try:

        pickle_in = open("booking.pickle", "rb")
        pickledata = pickle.load(pickle_in)
        bookingdata = pickledata.get('bookingdata')

    except:
        pass

    try:
        username = request.session["username"]
    except:
        pass

        #bookingdata[username] = {"username":username, "doctorname":doctorname, "timeslot": timeslot, "status": "NA"}
    #print(bookingdata)


    doctorusername = request.session["doctorusername"]
    print(doctorusername)
    for i in bookingdata:
        if doctorusername == bookingdata.get(i).get("doctorname"):
            d_name_list.append(bookingdata.get(i).get("username"))
            d_age_list.append(bookingdata.get(i).get("age"))
            d_address_list.append(bookingdata.get(i).get("address"))
            d_date_list.append(bookingdata.get(i).get("date"))
            d_time_list.append(bookingdata.get(i).get("timeslot"))
            d_message_list.append(bookingdata.get(i).get("message"))
            d_status_list.append(bookingdata.get(i).get("status"))
            

    request_list = list(zip(d_name_list,d_age_list,d_address_list,d_date_list,d_time_list,d_message_list,d_status_list))
    #print(request_list)

    if request.method == 'POST':

        try:
            pickle_in = open("booking.pickle", "rb")
            pickledata = pickle.load(pickle_in)
            bookingdata = pickledata.get('bookingdata')

        except:
            pass

        approvepatientname = request.POST.get('approvepatient')
        #print(approvepatientname)

        if 'acceptbutton' in request.POST:

            bookingdata.get(approvepatientname)["status"] = "Accepted"

        if 'rejectbutton' in request.POST:

            bookingdata.get(approvepatientname)["status"] = "Rejected"

    
        new_status = bookingdata.get(approvepatientname).get('status')

        d_name_list.clear()
        d_age_list.clear()
        d_address_list.clear()
        d_date_list.clear()
        d_time_list.clear()
        d_message_list.clear()
        d_status_list.clear()


        for i in bookingdata:
            if doctorusername == bookingdata.get(i).get("doctorname"):
                d_name_list.append(bookingdata.get(i).get("username"))
                d_age_list.append(bookingdata.get(i).get("age"))
                d_address_list.append(bookingdata.get(i).get("address"))
                d_date_list.append(bookingdata.get(i).get("date"))
                d_time_list.append(bookingdata.get(i).get("timeslot"))
                d_message_list.append(bookingdata.get(i).get("message"))
                d_status_list.append(bookingdata.get(i).get("status"))
                

        request_list = list(zip(d_name_list,d_age_list,d_address_list,d_date_list,d_time_list,d_message_list,d_status_list))
        print(request_list)
        pickle_out = open("booking.pickle", "wb")
        pickledata = {'bookingdata': bookingdata}
        pickle.dump(pickledata, pickle_out)
        pickle_out.close()

        return render(request, "doctordashboard.html", context={"request_list":request_list})

    return render(request, "doctordashboard.html", context={"request_list":request_list})
    #return render(request, "doctordashboard.html")

def patientpersonaldetails(request):
    try:
        pickle_in = open("patients.pickle", "rb")
        pickledata = pickle.load(pickle_in)
        registeredpatients = pickledata.get('registeredpatients')
        #print(registeredpatients)
    except:
        pass

    current_patient = request.session["username"]

    patient_email = registeredpatients.get(current_patient)["username"]
    patient_age = registeredpatients.get(current_patient)["age"]
    patient_phone = registeredpatients.get(current_patient)["phone"]
    patient_aadhaar = registeredpatients.get(current_patient)["aadhaar"]
    patient_pan = registeredpatients.get(current_patient)["pan"]
    patient_pic = file_name = "{}{}.jpg".format(os.path.join(BASE_DIR, 'myapp/static/'),patient_email)
    print(patient_pic)

    return render(request, "patientpersonaldetails.html",{"patient_email":patient_email,
        "patient_age":patient_age,
        "patient_phone":patient_phone,
        "patient_aadhaar":patient_aadhaar,
        "patient_pan":patient_pan,
        "patient_pic":patient_pic})

def patientdashboard(request):

    if 'calldoctor' in request.POST:
        return redirect('/videocall')

    if 'reporthistory' in request.POST:
        return redirect('/reporthistorypage')

    if 'patientpersonaldetails' in request.POST:
        return redirect("/patientpersonaldetails")

    if 'reportdoctor' in request.POST:
        return redirect("/reportdoctor")

    if 'ratedoctor' in request.POST:
        return redirect("/ratedoctor")

    bookingdata = {}
    doctors = [] #to return in select

    doctor_name_list = []
    time_slot_list = []
    status_list =[]

    #final_list = []

    if 'status' in request.POST:
        username = request.session["username"]
        try:
            pickle_in = open("booking.pickle", "rb")
            pickledata = pickle.load(pickle_in)
            bookingdata = pickledata.get('bookingdata')

        except:
            pass

        #bookingdata[username] = {"username":username, "doctorname":doctorname, "timeslot": timeslot, "status": "NA"}

        for i in bookingdata:
            if i == username:
                doctor_name_list.append(bookingdata.get(username).get("doctorname").split("@")[0])
                time_slot_list.append(bookingdata.get(username).get("timeslot"))
                status_list.append(bookingdata.get(username).get("status"))

        final_list = list(zip(doctor_name_list,time_slot_list,status_list))

        return render(request, "viewbookingstatus.html", context={"final_list":final_list})

    if 'logout' in request.POST:
        return redirect('/')

    try:
        pickle_in = open("doctors.pickle", "rb")
        pickledata = pickle.load(pickle_in)
        registereddoctors = pickledata.get('registereddoctors')

        for i in registereddoctors:
            doctors.append(i.split("@")[0])

    except:
        pass


    if request.method == 'POST':
        
        username = request.session["username"]

        name = request.POST.get('name')
        age = request.POST.get('age')
        address = request.POST.get('address')
        doctorname = request.POST.get('doctorname')
        # date = request.POST.get('date')
        # timeslot = request.POST.get('timeslot')
        # message = request.POST.get('message')

        #print("doctorname: "+doctorname)
        doctorname = doctorname+"@gmail.com"

        request.session["temp_booking_username"] = username
        request.session["temp_booking_name"] = name
        request.session["temp_booking_age"] = age
        request.session["temp_booking_address"] = address
        request.session["temp_booking_doctorname"] = doctorname

        

        return redirect("bookingpanel")

    return render(request, "patientdashboard.html", context={'register_doctor_list':doctors})

def viewbookingstatus(request):
    
    #if 'back' in request.POST:
        #return redirect('/')
    return render(request, "viewbookingstatus.html")

def reporthistorypage(request):

    all_generated_report_users = []

    try:
        pickle_in_report = open("patientreports.pickle", "rb")
        pickledata_report = pickle.load(pickle_in_report)

        current_patient_name = request.session["username"]

        for i in pickledata_report:
            if i == current_patient_name.split("@")[0]:
                all_generated_report_users.append(current_patient_name.split("@")[0])
    except:
        pass

    if request.method == "POST":
        reportemail = request.POST.get('reportemail')

        if reportemail.split("@")[0] not in all_generated_report_users:
            return render(request,"reporthistorypage.html",{"mymessage":"No report is available for you.","Flag":"True"})
        else:
            username = all_generated_report_users[0]
            prescription = pickledata_report.get(all_generated_report_users[0]).split(":")[0]
            doctorname = pickledata_report.get(all_generated_report_users[0]).split(":")[1]
            
            c = canvas.Canvas("prescription_report.pdf")
            
            line_x_start = 220
            line_width = 150
            line_y = 300

            c.setStrokeColorCMYK(0.68,0.44,0,0.41)
            c.setLineWidth(7)
            c.line(line_x_start, line_y,
                        line_x_start+line_width, line_y)

            c.drawImage(app_logo, line_x_start, line_y, width=line_width, 
                             preserveAspectRatio=True, mask='auto')

            c.drawString(100, 600, "Patient Name : "+username)
            c.drawString(100, 550, "Prescription : "+prescription)
            c.drawString(100, 500, "Prescribed by Doctor : "+doctorname.split("@")[0])
            c.save()

            os.startfile("prescription_report.pdf")

            return render(request,"reporthistorypage.html",{"mymessage":"Report Generated.","Flag":"True"})

    return render(request, "reporthistorypage.html")

def bookingpanel(request):
    bookingdata = {}
    doctor_name_list = []
    time_slot_list= []
    status_list = []

    doctorname = request.session["temp_booking_doctorname"]
    try:
        pickle_in = open("doctors.pickle", "rb")
        pickledata = pickle.load(pickle_in)
        registereddoctors = pickledata.get('registereddoctors')
        print(registereddoctors)
    except:
        pass

    all_timeslots_available = ["10 am to 11 am", "11 am to 12 am", "1 pm to 2 pm", "5 pm to 6 pm", "6 pm to 7 pm", "7 pm to 8 pm"]
    current_booked_slots = registereddoctors.get(doctorname).get("booked_slots")
    
    current_available_slots = []

    for i in all_timeslots_available:
        if i not in current_booked_slots:
            current_available_slots.append(i)

    print(current_available_slots)

    if request.method == 'POST':



        username = request.session["temp_booking_username"]
        name = request.session["temp_booking_name"]
        age = request.session["temp_booking_age"]
        address = request.session["temp_booking_address"]
        doctorname = request.session["temp_booking_doctorname"]
        
        date = request.POST.get('date')
        timeslot = request.POST.get('timeslot')
        message = request.POST.get('message')

        print(timeslot)
        
        print(doctorname)
        doctor_booking_time_slot = registereddoctors.get(doctorname).get("booked_slots")
        doctor_booking_time_slot.append(timeslot)
        registereddoctors.get(doctorname)["booked_slots"] = doctor_booking_time_slot
        

        try:
            pickle_in_booking = open("booking.pickle", "rb")
            pickledata_booking = pickle.load(pickle_in_booking)
            bookingdata = pickledata_booking.get('bookingdata')

        except:
            pass

        bookingdata[username] = {"username":username, "doctorname":doctorname, "timeslot": timeslot, "status": "NA",
        "age":age, "address":address, "date":date, "message":message}

        for i in bookingdata:
            if i == username:
                doctor_name_list.append(bookingdata.get(username).get("doctorname"))
                time_slot_list.append(bookingdata.get(username).get("timeslot"))
                status_list.append(bookingdata.get(username).get("status"))

        final_list = list(zip(doctor_name_list,time_slot_list,status_list))
        print(final_list)

        

        pickle_out_booking = open("booking.pickle", "wb")
        pickledata_booking = {'bookingdata': bookingdata}
        pickle.dump(pickledata_booking, pickle_out_booking)
        pickle_out_booking.close()

        pickle_out = open("doctors.pickle", "wb")
        pickledata = {'registereddoctors': registereddoctors}
        pickle.dump(pickledata, pickle_out)
        pickle_out.close()

        #return render(request, "paymentpage.html", context={"final_list":final_list})
        #return redirect("paymentpage")
        return render(request,"bookingpanel.html",{"mymessage":"Booking Succesful.","Flag":"True"})


    return render(request, "bookingpanel.html",context={"current_available_slots":current_available_slots})