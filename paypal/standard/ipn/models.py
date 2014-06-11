#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
from paypal.standard.models import PayPalStandardBase
from paypal.standard.ipn.signals import *

import logging

log = logging.getLogger(__name__)


class PayPalIPN(PayPalStandardBase):
    """Logs PayPal IPN interactions."""
    format = u"<IPN: %s %s>"

    class Meta:
        db_table = "paypal_ipn"
        verbose_name = "PayPal IPN"

    def _postback(self):
        """Perform PayPal Postback validation."""
        request = urllib2.Request(self.get_endpoint(), "cmd=_notify-validate&%s" % self.query)
        rc = urllib2.urlopen(request, timeout=30).read()
        log.info("querying IPN: %s\nReturn Code was %s" % (self.query, rc))
        return rc

    def _verify_postback(self):
        if self.response != "VERIFIED":
            self.set_flag("Invalid postback. (%s)" % self.response)
            
    def send_signals(self):
        """Shout for the world to hear whether a txn was successful."""
        # Transaction signals:
        if self.is_transaction():
            if self.flag:
                payment_was_flagged.send(sender=self)
            else:
                payment_was_successful.send(sender=self)
        # Recurring payment signals:
        # XXX: Should these be merged with subscriptions?
        elif self.is_recurring():
            if self.is_recurring_create():
                recurring_create.send(sender=self)
            elif self.is_recurring_payment():
                recurring_payment.send(sender=self)
            elif self.is_recurring_cancel():
                recurring_cancel.send(sender=self)
        # Subscription signals:
        else:
            if self.is_subscription_cancellation():
                subscription_cancel.send(sender=self)
            elif self.is_subscription_signup():
                subscription_signup.send(sender=self)
            elif self.is_subscription_end_of_term():
                subscription_eot.send(sender=self)
            elif self.is_subscription_modified():
                subscription_modify.send(sender=self)
