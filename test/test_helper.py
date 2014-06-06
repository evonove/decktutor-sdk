import logging

# Logging
from decktutorsdk import decktutor

logging.basicConfig(level=logging.INFO)

# Credential
login = "test_user"
password = "test_password"

# Set credential for default api
decktutor.set_auth_config(username=login, password=password)
