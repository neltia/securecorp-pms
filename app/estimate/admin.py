from django.contrib import admin
from estimate.models import RegisteredDomain
from estimate.models import EstimateDoc, EstimateFile, EstimatePubNum

admin.site.register(RegisteredDomain)
admin.site.register(EstimateDoc)
admin.site.register(EstimateFile)
admin.site.register(EstimatePubNum)
