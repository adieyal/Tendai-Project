import models

def process_signal(sender, submission, **kwargs):
    try:
        device = models.Device.objects.get(device_id=submission.device_id)
        community_worker = device.community_worker
    except models.Device.DoesNotExist:
        device = None
        community_worker = None
        
    models.SubmissionWorkerDevice.objects.create(
        submission=submission,
        device=device,
        community_worker=community_worker
    )
    
