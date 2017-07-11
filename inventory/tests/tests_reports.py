from django.test import TestCase

## Create your tests here.
# class JobTest(TestCase):
#         p_aanbieder_2 = ProfileAanbieder(user=u_aanbieder_2, first_name='Voor', last_name='Aanbieder 2')
#         p_aanbieder_2.save()
#         p_zorgvrager = ProfileZorgVrager(user=u_zorgvrager, first_name='Voor', last_name='ZorgVrager')
#         p_zorgvrager.save()

#         j = Job(title='test', profile=p_zorgvrager)
#         j.save()
#         self.assertEqual('test', j.__unicode__())
#         self.assertEqual(u'/jobs/test', j.get_absolute_url())

#         q = Quote(job=j, profile=p_aanbieder, description='aanbieding')
#         q.save()
#         self.assertEqual('aanbieding', q.__unicode__())
#         self.assertEqual(q.get_absolute_url(), u'/quotes/{}'.format(q.id))
