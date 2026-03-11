import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from risks.models import Risk
class Command(BaseCommand):
    help = 'Sends email reminders for risks due within the next 7 days'
    def handle(self, *args, **options):
        today = now().date()
        reminder_window = today + timedelta(days=7)
        approaching_risks = Risk.objects.filter(
            status__in=['open', 'in_progress'],
            due_date__range=[today, reminder_window]
        ).prefetch_related('assigned_to')
        if not approaching_risks.exists():
            self.stdout.write(self.style.SUCCESS('No risks due within the next 7 days.'))
            return
        count = 0
        for risk in approaching_risks:
            assigned_users = risk.assigned_to.filter(email__isnull=False).exclude(email='')
            if not assigned_users.exists():
                continue
            recipient_list = [user.email for user in assigned_users]
            subject = f'[GMS Reminder] Risk Due Soon: {risk.name}'
            message = (
                f"Hello,\n\n"
                f"This is an automated reminder that the following risk is approaching its due date:\n\n"
                f"  Risk Name: {risk.name}\n"
                f"  Due Date: {risk.due_date}\n"
                f"  Status: {risk.get_status_display()}\n"
                f"  Category: {risk.category.name if risk.category else 'N/A'}\n\n"
                f"Please log in to the Governance Management System to review and update the mitigation plan.\n\n"
                f"Regards,\nGMS System"
            )
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list,
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'Sent reminder for: {risk.name} to {", ".join(recipient_list)}'))
                count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to send reminder for {risk.name}: {str(e)}'))
        self.stdout.write(self.style.SUCCESS(f'Successfully sent reminders for {count} risks.'))
