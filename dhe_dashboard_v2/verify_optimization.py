
import time
import logging
import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.getcwd())

from core.data_loader import load_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_load_data_performance():
    print("Starting data load performance test...")
    start_time = time.time()
    
    try:
        # Mock streamlit cache to avoid error if run outside streamlit (though we use decorators)
        # Actually streamlit cache might complain if not running via streamlit run.
        # But let's try invoking it. If it fails due to st context, we might need to mock st.
        
        # We can mock streamlit module
        import streamlit as st
        # Verify if we are in streamlit
        
        data = load_data()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Data load completed in {duration:.2f} seconds.")
        
        if data:
            print("Data Packet Keys:", data.keys())
            for k, v in data.items():
                if isinstance(v, pd.DataFrame):
                    print(f"  {k}: {v.shape}")
                else:
                    print(f"  {k}: {type(v)}")
        else:
            print("Data packet is empty!")
            
    except Exception as e:
        print(f"Error during load_data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Mocking streamlit cache_data if necessary for script execution
    # Since we modified the code to use @st.cache_data, running this as a raw script might skip caching or error out if st is not initialized properly.
    # However, st.cache_data usually works as a passthrough if not in streamlit context OR requires a running loop.
    # Let's try running it.
    test_load_data_performance()
