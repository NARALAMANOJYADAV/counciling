from django.contrib import admin
from django.utils.html import format_html
from .models import StudentCounseling

@admin.register(StudentCounseling)
class StudentCounselingAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'academic_year', 'counselor_name',
        'get_pass_count', 'get_fail_count',
        'get_subjects_display', 'get_attendance_display'
    ]

    search_fields = [
        'student_name', 'counselor_name',
        'subject1', 'subject2', 'subject3', 'subject4', 'subject5',
        'attendance_percent1', 'attendance_percent2', 'attendance_percent3', 'attendance_percent4', 'attendance_percent5'
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        attendance_search = request.GET.get('attendance_search', '').strip()

        # Store for UI form
        self.attendance_search = attendance_search

        if attendance_search:
            try:
                attendance_val = float(attendance_search)
                filtered_ids = []
                for student in queryset:
                    latest_attendance = None
                    for i in reversed(range(1, 6)):
                        att = getattr(student, f'attendance_percent{i}', None)
                        if att is not None:
                            latest_attendance = float(att)
                            break
                    if latest_attendance is not None and abs(latest_attendance - attendance_val) < 0.05:
                        filtered_ids.append(student.id)
                queryset = queryset.filter(id__in=filtered_ids)
            except ValueError:
                pass  # Ignore if input is not a valid float

        return queryset

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Add attendance search UI to top right
        extra_context['attendance_search_form'] = format_html("""
            <div style="float:right;margin:10px 20px;">
                <form method="get">
                    <input type="text" name="attendance_search" value="{}" placeholder="Search by Attendance">
                    <input type="submit" value="Search">
                    <a href="?" style="margin-left:10px;">Clear</a>
                </form>
                <small style="color:gray;">Matches students with latest attendance ≈ entered value (±0.05)</small>
            </div>
        """, self.attendance_search if hasattr(self, 'attendance_search') else '')

        # Subject search-based pass/fail summary
        search_query = request.GET.get('q', '')
        search_query = search_query.strip().lower() if search_query else ''
        if search_query:
            subject_names = set()
            filtered_queryset = self.get_queryset(request)
            for student in filtered_queryset:
                for i in range(1, 6):
                    subject = getattr(student, f'subject{i}', '')
                    subject = subject.strip().lower() if subject else ''
                    if subject:
                        subject_names.add(subject)

            if search_query in subject_names:
                subject_pass = 0
                subject_fail = 0
                for student in filtered_queryset:
                    for i in range(1, 6):
                        subject = getattr(student, f'subject{i}', '')
                        subject = subject.lower() if subject else ''
                        result = getattr(student, f'result{i}', '')
                        result = str(result or '')  # Convert None to empty string
                        if search_query in subject:
                            if result.upper() == 'P':
                                subject_pass += 1
                            elif result.upper() == 'F':
                                subject_fail += 1
                            break
                extra_context['title'] = format_html(
                    'Subject Summary → Passed: <span style="color:green">{}</span> | '
                    'Failed: <span style="color:red">{}</span> | Total: {}',
                    subject_pass, subject_fail, subject_pass + subject_fail
                )

        return super().changelist_view(request, extra_context=extra_context)

    def get_pass_count(self, obj):
        return sum(1 for i in range(1, 6) if (str(getattr(obj, f'result{i}', '') or '')).upper() == 'P')

    get_pass_count.short_description = 'Passes'

    def get_fail_count(self, obj):
        return sum(1 for i in range(1, 6) if (str(getattr(obj, f'result{i}', '') or '')).upper() == 'F')

    get_fail_count.short_description = 'Fails'

    def get_subjects_display(self, obj):
        subjects = []
        for i in range(1, 6):
            subject = getattr(obj, f'subject{i}', '')
            result = getattr(obj, f'result{i}', '')
            # Ensure result is not None before calling .upper()
            result = str(result or '')  # Convert None to empty string
            if subject and result:
                color = 'green' if result.upper() == 'P' else 'red' if result.upper() == 'F' else 'black'
                subjects.append(f"{subject}: <strong style='color:{color}'>{result.upper()}</strong>")
        return format_html("<br>".join(subjects) if subjects else 'No subjects')

    get_subjects_display.short_description = 'Subjects & Results'

    def get_attendance_display(self, obj):
        latest_attendance = None
        for i in reversed(range(1, 6)):
            att = getattr(obj, f'attendance_percent{i}', None)
            if att is not None:
                latest_attendance = att
                break
        if latest_attendance is not None:
            color = 'green' if float(latest_attendance) >= 75 else 'orange' if float(latest_attendance) >= 60 else 'red'
            return format_html('<span style="color:{}">{}</span>', color, latest_attendance)
        return '-'

    get_attendance_display.short_description = 'Latest Attendance %'
