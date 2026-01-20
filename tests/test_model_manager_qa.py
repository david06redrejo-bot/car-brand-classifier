"""
tests/test_model_manager_qa.py

QA/Testing: Validate that the Application Layer accepts the fix.
"""
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_model_manager_integration():
    """
    QA Test: Validate ModelManager Integration after structural changes.
    
    Requirements:
    1. Initialize the app.services.model_manager.ModelManager singleton
    2. Load Test: Call manager.load_domain('cars')
    3. Assertion:
       - Check that the returned dictionary is NOT None
       - Verify it contains keys: 'svm', 'kmeans', 'scaler', 'classes'
    4. Report: Print "SUCCESS: System Recovered" or "FAILURE: [Reason]"
    """
    try:
        print("=" * 60)
        print("QA TEST: ModelManager Integration Validation")
        print("=" * 60)
        
        # Step 1: Initialize ModelManager Singleton
        print("\n[1/4] Instantiating ModelManager singleton...")
        from app.services.model_manager import ModelManager
        manager = ModelManager()
        print("[OK] ModelManager instantiated successfully")
        
        # Step 2: Load Test - Call load_domain('cars')
        print("\n[2/4] Loading domain: 'cars'...")
        models = manager.load_domain('cars')
        print("[OK] load_domain('cars') completed")
        
        # Step 3a: Assertion - Check NOT None
        print("\n[3/4] Validating returned models...")
        if models is None:
            raise AssertionError("load_domain returned None - Models not available")
        print("[OK] Models dictionary is NOT None")
        
        # Step 3b: Verify Keys
        print("\n[4/4] Verifying model keys...")
        required_keys = ['svm', 'kmeans', 'scaler', 'classes']
        missing_keys = [key for key in required_keys if key not in models]
        
        if missing_keys:
            raise AssertionError(f"Missing required keys: {missing_keys}")
        
        print(f"[OK] All required keys present: {list(models.keys())}")
        
        # Additional Validation: Verify models are not None
        print("\n[EXTRA] Verifying model objects are loaded...")
        for key in required_keys:
            if models[key] is None:
                raise AssertionError(f"Model '{key}' is None")
            print(f"  [OK] {key}: {type(models[key]).__name__}")
        
        # Step 4: Report Success
        print("\n" + "=" * 60)
        print("SUCCESS: System Recovered")
        print("=" * 60)
        print("\n[PASS] ModelManager successfully loads all required artifacts:")
        print(f"   - SVM Classifier: {type(models['svm']).__name__}")
        print(f"   - K-Means Codebook: {type(models['kmeans']).__name__}")
        print(f"   - StandardScaler: {type(models['scaler']).__name__}")
        print(f"   - Class Labels: {models['classes']}")
        print("\n[RESULT] The Application Layer is fully operational.")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("FAILURE: [Reason]")
        print("=" * 60)
        print(f"\n[ERROR] {type(e).__name__}: {str(e)}")
        
        import traceback
        print("\n[Stack Trace]")
        traceback.print_exc()
        
        print("\n[INFO] Possible Causes:")
        print("   - Models not trained yet (run train/train_model.py)")
        print("   - Model paths misconfigured in core/config.py")
        print("   - Missing model files in models/cars/")
        
        return False

if __name__ == '__main__':
    success = test_model_manager_integration()
    sys.exit(0 if success else 1)
