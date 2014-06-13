import django.dispatch

on_submission = django.dispatch.Signal(providing_args=["submission"])
