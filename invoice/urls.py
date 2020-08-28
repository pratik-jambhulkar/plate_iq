from rest_framework.routers import DefaultRouter

from invoice.views import UserViewSet, InvoiceViewSet

router = DefaultRouter(trailing_slash=False)

router.register('users', UserViewSet, basename='users')
router.register('invoices', InvoiceViewSet, basename='invoices')
urlpatterns = router.urls
