from rest_framework.routers import DefaultRouter

from invoice.views import UserViewSet, InvoiceViewSet, CompanyViewSet

router = DefaultRouter(trailing_slash=False)

router.register('users', UserViewSet, basename='users')
router.register('invoices', InvoiceViewSet, basename='invoices')
router.register('companies', CompanyViewSet, basename='companies')
urlpatterns = router.urls
