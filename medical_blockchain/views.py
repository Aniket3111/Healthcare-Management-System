from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django import forms
import pandas as pd
import numpy as np
import hashlib
import io
from cryptography.fernet import Fernet
import csv
from csv import writer
from io import TextIOWrapper
from blockapp.models import D_Register,EncryptedCSV,Patient_Data
from blockapp.forms import CSVUploadForm
from ftplib import FTP
import joblib
from sklearn.ensemble import GradientBoostingRegressor
# from sklearn.externals import joblib

def upload(request):
    f=CSVUploadForm()
    return render(request, 'upload.html',{'form':f})

def uploadfile(request):
    hashed=[]
  
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Read the uploaded file
            csv_f= request.FILES['csv_file']
            df =pd.read_csv(csv_f)
            # Split the DataFrame into three equal parts
            dfs = np.array_split(df, 3)

            # Print the length of each split DataFrame
            for split_df in dfs:
                print(len(split_df))
            def create_hash(df):

            # Convert the DataFrame to a bytes object
                df_bytes = df.to_csv(index=False).encode()

            # Compute the SHA-256 hash of the DataFrame
                sha256_hash = hashlib.sha256(df_bytes).hexdigest()
                #print(sha256_hash)
                hashed.append(sha256_hash)
                # print("SHA-256 hash of the DataFrame is: {}".format(sha256_hash))

            for df in dfs:
                create_hash(df)
                
             
            df1=dfs[0]
            df2=dfs[1]
            df3=dfs[2]    
            # Generate a new encryption key
            key = Fernet.generate_key()
            
            with open('encryption_key.bin', 'wb') as f:
                f.write(key)

            # Create a Fernet instance with the key
            fernet = Fernet(key)


            # # Convert DataFrame to bytes and encrypt
            data_bytes1 = df1.to_csv(index=False).encode()
            data_bytes2 = df2.to_csv(index=False).encode()
            data_bytes3 = df3.to_csv(index=False).encode()
            # Concatenate the encrypted data and write it to a new file
            # data_bytes = data_bytes1 + data_bytes2 + data_bytes3

            encrypted_bytes1 = fernet.encrypt(data_bytes1)
            encrypted_bytes2 = fernet.encrypt(data_bytes2)
            encrypted_bytes3 = fernet.encrypt(data_bytes3)

            with open('encrypted_file1.bin', 'wb') as f:
                f.write(encrypted_bytes1)
            with open('encrypted_file2.bin', 'wb') as f:
                f.write(encrypted_bytes2)
            with open('encrypted_file3.bin', 'wb') as f:
                f.write(encrypted_bytes3)  
            
            obj=EncryptedCSV(encrypted_data_1=encrypted_bytes1,encrypted_data_2=encrypted_bytes2,encrypted_data_3=encrypted_bytes3)
            obj.save()

                 
    return render(request,'block.html',{'hash1':hashed[0],'hash2':hashed[1],'hash3':hashed[2]})            
    
    
    
    


def block(request):
    return render(request,'block.html')

def blk(request):

            ftp = FTP('ftp.drivehq.com')
            ftp.login(user='', passwd='')  #enter your drivehq mail id and password
            
            ftp.cwd('/ML_BLOCK1')
            file = open(r"", 'rb')  # replace 'path/to/local/file' with the path to your local file
            ftp.storbinary('STOR encrypted_file1.bin', file)  # replace 'file.txt' with the desired filename on DriveHQ      
             
            ftp.cwd('/ML_BLOCK2')
            file = open(r"", 'rb')  # replace 'path/to/local/file' with the path to your local file
            ftp.storbinary('STOR encrypted_file2.bin', file)  # replace 'file.txt' with the desired filename on DriveHQ                
                                
            ftp.cwd('/ML_BLOCK3')
            file = open(r"", 'rb')  # replace 'path/to/local/file' with the path to your local file
            ftp.storbinary('STOR encrypted_file3.bin', file)  # replace 'file.txt' with the desired filename on DriveHQ   
    
            return render(request,'success.html')
    


def download(request):
    ftp = FTP('ftp.drivehq.com')
    ftp.login(user='', passwd='') #enter your drivehq mail id and password
    ftp.cwd('/ML_BLOCK1')
    # replace 'file.txt' with the desired filename on DriveHQ
    filename1 = 'encrypted_file1.bin'
    
    ftp.cwd('/ML_BLOCK2')
    # replace 'file.txt' with the desired filename on DriveHQ
    filename2 = 'encrypted_file2.bin'
    
    ftp.cwd('/ML_BLOCK3')
    # replace 'file.txt' with the desired filename on DriveHQ
    filename3 = 'encrypted_file3.bin'
    
    with open('encrypted_file1.bin', 'rb') as f:
        encrypted_bytes1 = f.read()

    with open('encrypted_file2.bin', 'rb') as f:
        encrypted_bytes2 = f.read()

    with open('encrypted_file3.bin', 'rb') as f:
        encrypted_bytes3 = f.read()
        
    with open('encryption_key.bin', 'rb') as f:
        key = f.read()    
    fernet = Fernet(key)
    
    # Decrypt and convert back to DataFrame
    decrypted_bytes1 = fernet.decrypt(encrypted_bytes1)
    decrypted_str1 = decrypted_bytes1.decode()
    decrypted_df1 = pd.read_csv(io.StringIO(decrypted_str1))

    decrypted_bytes2 = fernet.decrypt(encrypted_bytes2)
    decrypted_str2 = decrypted_bytes2.decode()
    decrypted_df2 = pd.read_csv(io.StringIO(decrypted_str2))

    decrypted_bytes3 = fernet.decrypt(encrypted_bytes3)
    decrypted_str3 = decrypted_bytes3.decode()
    decrypted_df3 = pd.read_csv(io.StringIO(decrypted_str3))
    
    df_final = pd.concat([decrypted_df1, decrypted_df2, decrypted_df3], axis=0, ignore_index=True)
    
    df_final.to_csv('patientdata.csv', index=False)
    
    return render(request,'healthprediction.html')
   
def healthpredict(request):
    return render(request,'healthprediction.html')

def replace_items(lis, a='F', b=0):
    for i, item in enumerate(lis):
        if(type(lis[i]) == type(lis)):
            lis[i] = replace_items(lis[i], a=a, b=b)
        else:
            if lis[i] == a:
                lis[i] = b
    return lis


def fetch(request):
    PatientID=request.POST.get("ID")

    obj = Patient_Data.objects.get(Patient_ID=PatientID)
    #print(obj.Name) 
    with open('') as file_obj:  #paientdata.csv path
        reader_obj = csv.reader(file_obj)
        for row in reader_obj:
            try:
                if row[0] == PatientID:
                    value = row
                    ID=value[0]
                    Name=value[1]
                    Address=value[2]
                    HAEMATOCRIT=value[3]
                    HAEMOGLOBINS=value[4]
                    ERYTHROCYTE=value[5]
                    LEUCOCYTE =value[6]
                    THROMBOCYTE= value[7]  
                    MCH=value[8]
                    MCHC=value[9]
                    MCV=value[10]
                    AGE=value[11]
                    SEX=value[12]
                    return render(request, "retrieve_patient.html",{"HAEMATOCRIT":HAEMATOCRIT,"HAEMOGLOBINS":HAEMOGLOBINS,"ERYTHROCYTE":ERYTHROCYTE,
                                          "LEUCOCYTE":LEUCOCYTE,"THROMBOCYTE":THROMBOCYTE,"MCH":MCH,
                                          "MCHC":MCHC,"MCV":MCV,"ID":ID,"AGE":AGE,"SEX":SEX,"Name":Name,"Address":Address})
                    
            except:
                continue
        else:
            messages.error(request, "Patient not found in our Database")
            return render(request, 'checkpatient.html') 
def feedbackform(request):
    return render(request,"feedbackform.html")

def replace_row_in_csv(file_path, new_data):
    # Read existing contents of the CSV file
    rows = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    # Iterate over the rows and check for a matching ID
    for i, row in enumerate(rows):
        if row[0] == new_data[0]:
            # Replace the matching row with the new data
            rows[i] = new_data
            break
    else:
        # If no match found, append the new data as a new row
        rows.append(new_data)

    # Write the updated list back to the CSV file
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
def health(request):
    ID=request.POST.get("ID")
    HAEMATOCRIT= request.POST.get('HAEMATOCRIT')
    HAEMOGLOBINS=request.POST.get('HAEMOGLOBINS')
    ERYTHROCYTE= request.POST.get('ERYTHROCYTE')
    LEUCOCYTE =request.POST.get('LEUCOCYTE')
    THROMBOCYTE= request.POST.get('THROMBOCYTE')  
    MCH=request.POST.get('MCH')
    MCHC=request.POST.get('MCHC')
    MCV= request.POST.get('MCV')
    AGE= request.POST.get('AGE')
    SEX=request.POST.get('SEX')
    Name=request.POST.get('Name')
    Address=request.POST.get("Address")
    cls=joblib.load('Random_Forest.sav')
    lis=[]
    lis.append(request.POST.get('HAEMATOCRIT'))
    lis.append(request.POST.get('HAEMOGLOBINS'))
    lis.append(request.POST.get('ERYTHROCYTE'))
    lis.append(request.POST.get('LEUCOCYTE'))
    lis.append(request.POST.get('THROMBOCYTE'))  
    lis.append(request.POST.get('MCH'))
    lis.append(request.POST.get('MCHC'))
    lis.append(request.POST.get('MCV'))
    lis.append(request.POST.get('AGE'))
    lis.append(request.POST.get('SEX'))
    

    # df = pd.read_csv(r"E:\Work\Final_Year_Project\medical_blockchain\patientdata.csv")
    

    
    # new = replace_items(lis, a='Female', b=0)
    # new = replace_items(lis, a='Male', b=1)
    data_array = np.asarray(lis)
    arr= data_array.reshape(1,-1)
    ans = cls.predict(arr)
    
    classterm=''
    finalans=''
    adm=''
    if(SEX=="0"):
        SEX="F"
    else:
        SEX="M"
    
    
    nlis=[]
    nlis.append(ID)
    nlis.append(Name)
    nlis.append(Address)
    nlis.extend(lis)
    nlis.pop()
    nlis.extend(SEX)
    nlis.extend(ans)

    replace_row_in_csv("",nlis)  # enter paientdata.csv path

    # with open('E:\Work\Final_Year_Project\medical_blockchain\patientdata.csv') as file_obj:
    #    reader_obj = csv.reader(file_obj)
        # for row in reader_obj:
                # if row[0] == ID:
                    # row=nlis[ID]

    # with open('E:\Work\Final_Year_Project\medical_blockchain\patientdata.csv', 'a') as f_object:
        # writer_object = writer(f_object)
        # writer_object.writerow(nlis)
        # f_object.close()
    if(ans=="out"):
      classterm='success'
      finalans='Normal'
      adm="doesn't"
    elif(ans=="in"):
      finalans = 'Abnormal'
      classterm='danger'
      adm=""
    obj=Patient_Data(HAEMATOCRIT=HAEMATOCRIT,HAEMOGLOBINS=HAEMOGLOBINS,ERYTHROCYTE=ERYTHROCYTE,
                                          LEUCOCYTE=LEUCOCYTE,THROMBOCYTE=THROMBOCYTE,MCH=MCH,
                                        MCHC=MCHC,MCV=MCV,Patient_ID=ID,AGE=AGE,SEX=SEX,Name=Name,Address=Address)
    obj.save()

    return render(request, "result.html",{'ans':finalans,"HAEMATOCRIT":HAEMATOCRIT,"HAEMOGLOBINS":HAEMOGLOBINS,"ERYTHROCYTE":ERYTHROCYTE,
                                          "LEUCOCYTE":LEUCOCYTE,"THROMBOCYTE":THROMBOCYTE,"MCH":MCH,
                                          "MCHC":MCHC,"MCV":MCV,"ID":ID,"AGE":AGE,"SEX":SEX,"classterm":classterm,"adm":adm,"Name":Name,"Address":Address})

   




# def hashcode(request):
#     # Read the CSV file into a DataFrame
#     df = pd.read_csv(r"C:\Users\LENOVO\Desktop\smallcsv.csv")

#     # Split the DataFrame into three equal parts
#     dfs = np.array_split(df, 3)

#     # Print the length of each split DataFrame
#     for split_df in dfs:
#         print(len(split_df))

#     def create_hash(df):

#     # Convert the DataFrame to a bytes object
#         df_bytes = df.to_csv(index=False).encode()

#     # Compute the SHA-256 hash of the DataFrame
#         sha256_hash = hashlib.sha256(df_bytes).hexdigest()
#         print(sha256_hash)

#         # print("SHA-256 hash of the DataFrame is: {}".format(sha256_hash))

#     for df in dfs:
#         create_hash(df)
        
    
    
    
    
    



# # Read the CSV file into a DataFrame
# df = pd.read_csv(r"C:\Users\LENOVO\Desktop\smallcsv.csv")

# # Split the DataFrame into three equal parts
# dfs = np.array_split(df, 3)

# # Print the length of each split DataFrame
# for split_df in dfs:
#     print(len(split_df))

# def create_hash(df):

# # Convert the DataFrame to a bytes object
#     df_bytes = df.to_csv(index=False).encode()

# # Compute the SHA-256 hash of the DataFrame
#     sha256_hash = hashlib.sha256(df_bytes).hexdigest()
#     print(sha256_hash)

#     # print("SHA-256 hash of the DataFrame is: {}".format(sha256_hash))

# for df in dfs:
#     create_hash(df)
def home(request):
    return render(request,'home.html')
def first(request):
    return render (request,'first.html')
def checkpatient(request):
    return render (request,'checkpatient.html')
def Dlogin(request):
    return render (request,'loginD.html')
def loginch(request):  
        status=False
        emailid=request.POST.get("emailid")
        password=request.POST.get("password")
        # print('username ',username, 'password ',password)
        #reg=Register.objects.all().filter(username=username,password=password)
        reg=D_Register.objects.all()
        for r in reg:
            if(r.emailid==emailid and r.password==password):
                status=True
                # print('here status ',status)
                break
        # print(status)
        if(status==True):
            f=CSVUploadForm()
            return render(request, 'upload.html',{'form':f})
            # return render(request,'upload.html')
        else:
            messages.error(request,"Incorrect username and password....Please try again...")
            return render(request,'loginD.html')
def block1(request):
    return render(request,'block1.html')
def signup(request):
    return render(request,'signup.html')  
def savedata(request):
    firstname=request.POST.get("firstname") 
    lastname=request.POST.get("lastname") 
    city=request.POST.get("city")
    mobilenumber=request.POST.get("mobilenumber")   
    emailid=request.POST.get("emailid")    
    password=request.POST.get("password")  
    confirm_password=request.POST.get("confirm_password")

    # f=request.FILES
    # filepath=f.get("filepath") 
    # # f=filepath.read()
    # # Generate a new encryption key
    # csv_file = TextIOWrapper(request.FILES[filepath].file, encoding='utf-8')
    # reader = csv.reader(csv_file)
    # for row in reader:
    #     data = ','.join(row)
    #     encrypted_data = D_Register()
    #     encrypted_data.set_data(data)
    #     encrypted_data.save()
    # return HttpResponse('Data uploaded successfully')
    # if(len(password)<8):
        # raise forms.ValidationError("Password is too short")
    def clean_username(emailid):
        if D_Register.objects.filter(emailid=emailid).exists():
            messages.error(request, 'This emailid already exists')
        return render(request,'signup.html') 
    clean_username(emailid)
    if (password != confirm_password):
        messages.error(request, 'Password does not match confirm Password')
        return render(request,'signup.html') 
    if(len(password)<8):
        messages.error(request,"Password Length is small, Please enter more than 8 characters")
        return render(request,'signup.html')
    else:
        obj=D_Register(firstname=firstname,lastname=lastname,city=city,mobilenumber=mobilenumber,emailid=emailid,password=password)
        obj.save()
        D_Register.objects.all()
        return render(request,'loginD.html')