from openrosa import models

def read_file():
    f = open("openrosa/streets")
    for line in f:
        yield line.strip().split("|")

for street_name, prefix in read_file(): 
    print street_name, prefix
    submissions = models.ORFormSubmission.objects.filter(
        property_street_name__istartswith=prefix, 
        property_area="factreton"
    )

    for a in submissions:
        c, _ = models.ORFormSubmissionCorrections.objects.get_or_create(submission=a)
        c.street_address = street_name
        c.save()
