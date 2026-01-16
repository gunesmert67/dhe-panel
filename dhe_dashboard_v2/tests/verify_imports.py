
import sys
import os
import importlib


# Set up path to include root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Verifying imports...")

try:
    modules_to_test = [
        "components.styles",
        "components.placeholders",
        "components.dashboard_financials",
        "components.dashboard_charts",
        "components.customer_tabs",
        "views.landing_page",
        "views.integrated_dashboard",
        "app"
    ]

    for module_name in modules_to_test:
        importlib.import_module(module_name)
        print(f"Successfully imported {module_name}")
    
    print("VERIFICATION SUCCESSFUL")

except ImportError as e:
    print(f"VERIFICATION FAILED: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
