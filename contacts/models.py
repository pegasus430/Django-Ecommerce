from __future__ import unicode_literals

from django.db import models

from defaults.helpers import get_model_fields
from xero_local import api as xero_api

from .countries import COUNTRY_CHOICES, EU_COUNTRIES

import logging
logger = logging.getLogger(__name__)

class AbstractAddress(models.Model):
    business_name = models.CharField(max_length=100)
    contact_first_name = models.CharField(max_length=100, blank=True, null=True)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=100, blank=True, null=True)
    contact_mobile = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address1 = models.CharField(max_length=100, blank=True, null=True)
    address2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    remark = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    @property 
    def is_eu_country(self):
        if self.country in EU_COUNTRIES:
            return True
        else:
            return False

    @property 
    def contact_full_name(self):
        if self.contact_first_name:
            if self.contact_name:
                return u'{} {}'.format(self.contact_first_name, self.contact_name)
            else:
                return u'{}'.format(self.contact_first_name)
        else:
            if self.contact_name:
                return u'{}'.format(self.contact_name)
        
        return False

    def printing_address_list(self, include_phone=False):
        address_lines = []
        address_lines.append(self.business_name)

        if self.contact_full_name:
            address_lines.append(self.contact_full_name)
        
        if self.address1:
            address_lines.append(self.address1)

        if self.address2:
            address_lines.append(self.address2)

        if self.city:
            if self.postcode:
                address_lines.append(u'{} {}'.format(self.city, self.postcode))
            else:
                address_lines.append(u'{}'.format(self.city))
        else:
            if self.postcode:
                address_lines.append(u'{}'.format(self.postcode))

        address_lines.append(self.get_country_display())

        if include_phone:
            if self.contact_phone:
                address_lines.append(u'Tel: {}'.format(self.contact_phone))

            if self.contact_mobile:
                address_lines.append(u'Mob: {}'.format(self.contact_mobile))

        return address_lines

    def printing_address_newlines(self, include_phone=False):
        return '\n'.join(self.printing_address_list(include_phone=include_phone))


##############
## Contacts ##
##############

class Agent(AbstractAddress):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    def return_commission(self, amount):
        for tier in self.agentcommission_set.all().order_by('-from_amount'):
            if amount >= tier.from_amount:
                return round(amount / 100 * tier.percentage, 2)

        raise Exception('No known AgentoCommission Structure')

    def comission_owed(self):
        '''return a list of dicts with all of the unpaid comissions with order number, sales amount and total commission value'''
        commissions = []
        sales_total = 0.0

        orders = []
        for relation in self.relation_set.all().filter(salesorder__is_paid=True, salesorder__paid_commission=False):
            orders.extend(relation.salesorder_set.filter(is_paid=True, paid_commission=False))
        
        orders = list(set(orders))
        for order in orders:
            try:
                date_paid = order.paid_on_date.strftime('%d/%m/%Y')
            except AttributeError:
                date_paid = u'Unkown'

            commision_item = {u'order #': order.id,
                u'order data': order.created_at.strftime('%d/%m/%Y'),
                u'client name': order.client.business_name,
                u'sale total': order.total_order_value,
                u'date paid':  date_paid}
            commissions.append(commision_item)
            sales_total += order.total_order_value

        commission_total = self.return_commission(sales_total)
        return commissions, commission_total


class AgentCommission(models.Model):
    agent = models.ForeignKey('Agent')
    from_amount = models.FloatField(default=0.0)
    percentage = models.FloatField(default=0.0)

    class Meta:
        ordering = ('from_amount',)

    def __unicode__(self):
        return u'{} receives {} from {}'.format(
            self.agent.name,
            self.percentage,
            self.from_amount)



class RelationAddress(AbstractAddress):
    relation = models.ForeignKey('Relation')
    default = models.BooleanField(default=False)

    def __unicode__(self):
        return '{} {} {}'.format(
            self.relation,
            self.address1,
            self.city)

    def save(self, *args, **kwargs):
        ## there should only be 1 default
        try:
            RelationAddress.objects.get(
                relation=self.relation,
                default=True)
        except RelationAddress.MultipleObjectsReturned:
            raise Exception('There can only be 1 default address')
        except RelationAddress.DoesNotExist:
            pass
        super(RelationAddress, self).save(*args, **kwargs)
        

class Relation(AbstractAddress):
    VAT_REGIME_CHOICES = (
        ('NONE', 'Non-EU'),
        ('ECZROUTPUT', 'With EU VAT-number'),
        ('OUTPUT2', 'Default'),
    )
    is_supplier = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    vat_number = models.CharField(max_length=100, blank=True, null=True)
    vat_regime = models.CharField(max_length=20, default='OUTPUT2', choices=VAT_REGIME_CHOICES)
    payment_days = models.IntegerField(default=0, verbose_name="Days to pay invoice")
    agent = models.ForeignKey(Agent, blank=True, null=True)
    _xero_contact_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ('business_name',)
    
    def __unicode__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        ## Update/Create Xero
        try:               
            response = xero_api.update_create_relation(self)
            if response != self._xero_contact_id:
                self._xero_contact_id = response
        except Exception as e:
            if 'is already assigned to another contact' in unicode(e):
                self._xero_contact_id = xero_api.find_relation_id(self.business_name)
            else:
                logger.error('Failed to save contact {} due to {}'.format(self.id, e))
                raise

        ## Run your save
        super(Relation, self).save(*args, **kwargs)

        ## Auto-create/update the RelationAddress
        address, created = RelationAddress.objects.get_or_create(
            relation=self,
            default=True)

        dont_compare_fields = ['is_client', 'is_supplier', 'vat_number', 'agent_id']
        compare_fields = [item for item in get_model_fields(self) if item not in dont_compare_fields]
        for field in compare_fields:
            set_value = getattr(self, field)
            setattr(address, field, set_value)
        address.save()

    
class OwnAddress(AbstractAddress):
    company_name = models.CharField(max_length=100)
    vat = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return '{} {} {}'.format(
            self.company_name,
            self.address1,
            self.city)
    
