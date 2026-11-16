from django.test import TestCase
from django.urls import reverse


class RegisterFeatureTests(TestCase):
    def test_register_template_uses_feature_assets(self):
        response = self.client.get(reverse('register:register'))
        self.assertTemplateUsed(response, 'register/register.html')
        self.assertContains(response, 'css/register/register.css')
        self.assertContains(response, 'js/register/register.js')
