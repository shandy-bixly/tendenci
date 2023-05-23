from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Calculate and grant diamond certifications.
    
    Set a daily cron job:
    1 20 * * * /opt/venvs/venv_t14/bin/python /opt/webapps/orgs/tendenci_site/manage.py check_and_grant_diamonds
    """
    
    def handle(self, *args, **options):
        from tendenci.apps.trainings.models import (Certification,
                                                    Transcript, UserCertData)

        for cert in Certification.objects.filter(enable_diamond=True):
            print('Processing ', cert)
            users = User.objects.filter(id__in=Transcript.objects.filter(certification_track=cert,
                                                                         ).values_list('user_id', flat=True))
            for user in users:
                print('.... for ', user)
                cert_data, created = UserCertData.objects.get_or_create(
                                        user=user,
                                        certification=cert)
                if not cert_data.certification_dt:
                    # check if requirements are all met, so that we can mark it as completed by setting certification_dt
                    if cert.is_requirements_met(user):
                        cert_data.certification_dt = date.today()
                        cert_data.save()
                    continue
                
                d_number = cert_data.get_next_d_number()
                if cert.is_requirements_met(user, diamond_number=d_number):
                    if d_number == 1:
                        # has it been one year since certification date
                        if  cert_data.certification_dt + relativedelta(months=cert.period) <= date.today():
                            setattr(cert_data, f'diamond_{d_number}_dt', date.today())
                            cert_data.save()
                    else:
                        last_diamond_date = getattr(cert_data, f'diamond_{d_number - 1}_dt')
                        if last_diamond_date + relativedelta(months=cert.diamond_period) <= date.today():
                            setattr(cert_data, f'diamond_{d_number}_dt', date.today())
                            cert_data.save()
