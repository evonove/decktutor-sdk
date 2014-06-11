import logging

# Logging
from decktutorsdk.api import api_factory

logging.basicConfig(level=logging.INFO)

# Credential
login = "test_user"
password = "test_password"

# Set credential for default api
api_factory.configure(username=login, password=password)
