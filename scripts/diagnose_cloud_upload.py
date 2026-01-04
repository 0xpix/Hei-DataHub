#!/usr/bin/env python3
"""
Diagnostic script to test cloud upload functionality.
Helps debug why edits might not be updating in HeiBox.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_webdav_connection():
    """Test WebDAV connection and permissions."""
    print("\n" + "=" * 60)
    print("Testing WebDAV Connection")
    print("=" * 60)

    try:
        from hei_datahub.services.storage_manager import get_storage_backend

        storage = get_storage_backend()
        print(f"✓ Storage backend created: {type(storage).__name__}")

        # Test listing
        try:
            entries = storage.listdir("")
            print(f"✓ Can list files: {len(entries)} entries found")
            for entry in entries[:5]:  # Show first 5
                print(f"  - {entry.name} ({'dir' if entry.is_dir else 'file'})")
        except Exception as e:
            print(f"✗ Cannot list files: {e}")
            return False

        # Test write capability with a test file
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            tmp.write("test upload")
            tmp_path = tmp.name

        try:
            test_remote_path = "_test_upload.txt"
            print(f"\nAttempting test upload to: {test_remote_path}")
            storage.upload(Path(tmp_path), test_remote_path)
            print("✓ Test upload successful")

            # Try to delete test file
            try:
                storage.delete(test_remote_path)
                print("✓ Test file deleted (cleanup successful)")
            except Exception:
                print("⚠ Could not delete test file (may need manual cleanup)")

            return True

        except Exception as e:
            print(f"✗ Test upload failed: {e}")
            print("\nThis suggests you don't have WRITE permissions.")
            print("Check your HeiBox folder permissions and auth settings.")
            return False
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        print(f"✗ Storage backend error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dataset_edit_simulation():
    """Simulate editing a dataset's metadata."""
    print("\n" + "=" * 60)
    print("Testing Dataset Edit Simulation")
    print("=" * 60)

    try:
        import os
        import tempfile

        import yaml

        from hei_datahub.services.storage_manager import get_storage_backend

        storage = get_storage_backend()

        # List datasets
        entries = storage.listdir("")
        datasets = [e for e in entries if e.is_dir]

        if not datasets:
            print("⚠ No datasets found in cloud storage")
            return False

        # Use first dataset for testing
        test_dataset = datasets[0].name
        print(f"\nTesting with dataset: {test_dataset}")

        # Download current metadata
        metadata_path = f"{test_dataset}/metadata.yaml"
        print(f"Downloading: {metadata_path}")

        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.yaml') as tmp:
            storage.download(metadata_path, tmp.name)
            download_path = tmp.name

        # Parse metadata
        with open(download_path, encoding='utf-8') as f:
            metadata = yaml.safe_load(f)

        print(f"Current metadata name: {metadata.get('name', 'N/A')}")

        # Simulate edit: add a timestamp comment
        from datetime import datetime
        metadata['_test_edit'] = f"Edited at {datetime.now().isoformat()}"

        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml', encoding='utf-8') as tmp:
            yaml.dump(metadata, tmp, sort_keys=False, allow_unicode=True)
            upload_path = tmp.name

        try:
            # Upload
            print(f"Uploading modified metadata to: {metadata_path}")
            storage.upload(Path(upload_path), metadata_path)
            print("✓ Upload successful!")

            # Verify by re-downloading
            print("\nVerifying upload...")
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.yaml') as tmp:
                storage.download(metadata_path, tmp.name)
                verify_path = tmp.name

            with open(verify_path, encoding='utf-8') as f:
                verify_metadata = yaml.safe_load(f)

            if '_test_edit' in verify_metadata:
                print(f"✓ Verification successful: {verify_metadata['_test_edit']}")

                # Clean up test field
                del metadata['_test_edit']
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml', encoding='utf-8') as tmp:
                    yaml.dump(metadata, tmp, sort_keys=False, allow_unicode=True)
                    cleanup_path = tmp.name

                storage.upload(Path(cleanup_path), metadata_path)
                print("✓ Test field removed (cleanup successful)")
                os.unlink(cleanup_path)

                return True
            else:
                print("✗ Verification failed: _test_edit field not found")
                return False

        finally:
            os.unlink(download_path)
            os.unlink(upload_path)
            try:
                os.unlink(verify_path)
            except Exception:
                pass

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_index_cloud_detection():
    """Test if index properly detects cloud vs local datasets."""
    print("\n" + "=" * 60)
    print("Testing Index Cloud Detection")
    print("=" * 60)

    try:
        from hei_datahub.services.fast_search import get_all_indexed

        results = get_all_indexed()

        cloud_count = sum(1 for r in results if r.get("metadata", {}).get("is_remote", False))
        local_count = sum(1 for r in results if not r.get("metadata", {}).get("is_remote", False))

        print(f"Total indexed: {len(results)}")
        print(f"Cloud datasets: {cloud_count}")
        print(f"Local datasets: {local_count}")

        if local_count > 0:
            print("\n⚠ Warning: Local datasets found in index")
            print("These will now be hidden in the TUI (cloud-only mode)")

        if cloud_count == 0:
            print("\n⚠ Warning: No cloud datasets found in index")
            print("Try running: python scripts/rebuild_index.py")

        return True

    except Exception as e:
        print(f"✗ Index test failed: {e}")
        return False

def main():
    """Run all diagnostic tests."""
    print("=" * 60)
    print("Cloud Upload Diagnostics")
    print("=" * 60)

    tests = [
        ("WebDAV Connection & Permissions", test_webdav_connection),
        ("Dataset Edit Simulation", test_dataset_edit_simulation),
        ("Index Cloud Detection", test_index_cloud_detection),
    ]

    results = []
    for name, test_func in tests:
        result = test_func()
        results.append(result)

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for (name, _), result in zip(tests, results):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    passed = sum(results)
    total = len(results)

    print()
    if passed == total:
        print(f"✓ All diagnostics passed ({passed}/{total})")
        print("\nCloud upload should be working correctly.")
        print("If you still have issues:")
        print("  1. Check logs: ~/.local/share/Hei-DataHub/logs/hei-datahub.log")
        print("  2. Run: python -m hei_datahub auth doctor")
        return 0
    else:
        print(f"✗ Some diagnostics failed ({passed}/{total} passed)")
        print("\nPlease fix the failed tests before using cloud edit.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
