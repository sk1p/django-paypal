from django.conf.urls import url, patterns

urlpatterns = patterns('paypal.standard.ipn.views',
    url(r'^$', 'ipn', name="paypal-ipn"),
)
