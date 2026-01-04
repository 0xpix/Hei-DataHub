"""Dataset reindexing command.

Handlers return integer exit codes and avoid terminating the process.
"""


def handle_reindex(args) -> int:
    """Handle the reindex subcommand - fetches from WebDAV cloud storage.

    Returns:
        int: 0 on success, 1 if errors occurred
    """
    import yaml

    from hei_datahub.infra.db import ensure_database, get_connection
    from hei_datahub.infra.index import upsert_dataset
    from hei_datahub.services.storage_manager import get_storage_backend

    print("Reindexing datasets from WebDAV cloud storage...")

    # Ensure database exists
    ensure_database()

    # Clear existing index
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets_store")
    cursor.execute("DELETE FROM datasets_fts")
    conn.commit()
    conn.close()
    print("✓ Cleared local index\n")

    try:
        # Get WebDAV storage backend
        storage = get_storage_backend(force_reload=True)
        print(f"✓ Connected to WebDAV: {storage.library}")

        # List all dataset folders from WebDAV
        entries = storage.listdir("")
        dataset_folders = [e.name for e in entries if e.is_dir and not e.name.startswith('.')]

        if not dataset_folders:
            print("No datasets found on WebDAV storage.")
            return 0

        print(f"Found {len(dataset_folders)} datasets on WebDAV\n")

        count = 0
        errors = []

        for dataset_id in dataset_folders:
            try:
                # Download metadata.yaml from WebDAV
                metadata_path = f"{dataset_id}/metadata.yaml"

                if not storage.exists(metadata_path):
                    errors.append(f"{dataset_id}: metadata.yaml not found")
                    continue

                # Download to temp file and read
                import tempfile
                from pathlib import Path

                with tempfile.NamedTemporaryFile(mode='w+', suffix='.yaml', delete=False) as f:
                    temp_path = f.name

                storage.download(metadata_path, temp_path)
                metadata_content = Path(temp_path).read_text()
                Path(temp_path).unlink()

                metadata = yaml.safe_load(metadata_content)

                # Fix legacy field name: 'name' → 'dataset_name'
                if metadata and 'name' in metadata and 'dataset_name' not in metadata:
                    metadata['dataset_name'] = metadata.pop('name')

                if metadata:
                    upsert_dataset(dataset_id, metadata)
                    count += 1
                    print(f"  ✓ Indexed: {dataset_id}")
                else:
                    errors.append(f"{dataset_id}: Empty or invalid metadata")

            except Exception as e:
                errors.append(f"{dataset_id}: {str(e)}")
                print(f"  ✗ Failed: {dataset_id} - {str(e)}")

        print(f"\n✓ Successfully indexed {count} dataset(s) from WebDAV")

        if errors:
            print(f"\n⚠ Encountered {len(errors)} error(s):")
            for error in errors:
                print(f"  • {error}")
            return 1
        else:
            print("All datasets indexed successfully!")
            return 0

    except Exception as e:
        print(f"\n❌ Reindex failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


        if not dataset_folders:
            print("No datasets found on WebDAV storage.")
            return 0

        print(f"Found {len(dataset_folders)} datasets on WebDAV\n")

        for dataset_id in dataset_folders:
            try:
                # Download metadata.yaml from WebDAV
                metadata_path = f"{dataset_id}/metadata.yaml"

                if not storage.file_exists(metadata_path):
                    errors.append(f"{dataset_id}: metadata.yaml not found")
                    continue

                # Read metadata content
                metadata_content = storage.read_text(metadata_path)
                metadata = yaml.safe_load(metadata_content)

                if metadata:
                    upsert_dataset(dataset_id, metadata)
                    count += 1
                    print(f"  ✓ Indexed: {dataset_id}")
                else:
                    errors.append(f"{dataset_id}: Empty or invalid metadata")

            except Exception as e:
                errors.append(f"{dataset_id}: {str(e)}")
                print(f"  ✗ Failed: {dataset_id} - {str(e)}")

        print(f"\n✓ Successfully indexed {count} dataset(s) from WebDAV")

        if errors:
            print(f"\n⚠ Encountered {len(errors)} error(s):")
            for error in errors:
                print(f"  • {error}")
            return 1
        else:
            print("All datasets indexed successfully!")
            return 0

    except Exception as e:
        print(f"\n❌ Reindex failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
