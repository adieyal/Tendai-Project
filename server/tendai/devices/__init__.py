from signals import process_signal
from openrosa import signals

signals.on_submission.connect(process_signal, dispatch_uid="devices_on_submission")
