from django.db import models
from cryptography.fernet import Fernet

# Create your models here.
class D_Register(models.Model):
    firstname=models.CharField(max_length=100,default="")
    lastname=models.CharField(max_length=100,default="")
    city=models.CharField(max_length=100,default="")
    mobilenumber=models.BigIntegerField(default=0)
    emailid=models.EmailField(max_length=100,default="")
    password=models.CharField(max_length=100,default="")    


class EncryptedCSV(models.Model):
    encrypted_data_1 = models.BinaryField(default=b"")
    encrypted_data_2 = models.BinaryField(default=b"")
    encrypted_data_3 = models.BinaryField(default=b"")

class Patient_Data(models.Model):
    Patient_ID=models.IntegerField(default=0)
    Name=models.CharField(max_length=100,default="")
    Address=models.CharField(max_length=100,default="")
    HAEMATOCRIT=models.FloatField(default=0)
    HAEMOGLOBINS=models.FloatField(default=0)
    ERYTHROCYTE=models.FloatField(default=0)
    LEUCOCYTE =models.FloatField(default=0)
    THROMBOCYTE= models.FloatField(default=0)
    MCH=models.FloatField(default=0)
    MCHC=models.FloatField(default=0)
    MCV=models.FloatField(default=0)
    AGE=models.IntegerField(default=0)
    SEX=models.CharField(max_length=100,default="") 
    

# class EncryptedData(models.Model):
#     encrypted_field = models.BinaryField()

#     def set_data(self, data):
#         key = Fernet.generate_key()
#         f = Fernet(key)
#         encrypted_data = f.encrypt(data.encode())
#         self.encrypted_field = encrypted_data

    # def get_data(self):
    #     f = Fernet(key)
    #     decrypted_data = f.decrypt(self.encrypted_field).decode()
    #     return decrypted_data

    