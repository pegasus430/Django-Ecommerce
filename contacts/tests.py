from django.test import TestCase
from .models import Agent, AgentCommission

class ReturnComissionTestCase(TestCase):
    ''' test the retun_comission function to return the correct comissions in 3 tiers
    > 0 = 5%
    > 10000 = 10%
    > 20000 = 20%
    '''
    def setUp(self):
        self.agent = Agent.objects.create(
            name='TestAgent')

        AgentCommission.objects.create(
            agent=self.agent,
            from_amount=0.0,
            percentage=5.00,)

        AgentCommission.objects.create(
            agent=self.agent,
            from_amount=10000.0,
            percentage=10.00,)

        AgentCommission.objects.create(
            agent=self.agent,
            from_amount=20000.0,
            percentage=20.00,)

    def test_sale_st_10000(self):
        amount = 5000
        expected_comission = 250.00
        self.assertEqual(expected_comission, self.agent.return_commission(amount))

    def test_sale_eq_10000(self):
        amount = 10000
        expected_comission = 1000.00
        self.assertEqual(expected_comission, self.agent.return_commission(amount))

    def test_sale_st_20000(self):
        amount = 15000
        expected_comission = 1500.00
        self.assertEqual(expected_comission, self.agent.return_commission(amount))

    def test_sale_eq_20000(self):
        amount = 20000
        expected_comission = 4000.00
        self.assertEqual(expected_comission, self.agent.return_commission(amount))

    def test_sale_gt_20000(self):
        amount = 30000
        expected_comission = 6000.00
        self.assertEqual(expected_comission, self.agent.return_commission(amount))
