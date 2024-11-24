from django.views.debug import ExceptionReporter

class ErrorReporter(ExceptionReporter):
    def get_traceback_data(self):
        traceback_data = super().get_traceback_data()

        traceback_data['settings'] = None
        traceback_data['sys_path'] = None

        return traceback_data