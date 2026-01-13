# 0.60-beta

## TO FIX

## FIXED
- [x] When first launch the app, it installs the desktop version too (even when i'm testing with the uv env) (Fixed: Added check for repo root to skip auto-install when running from source/dev environment)
- [x] Crash on first run due to missing data directory (Fixed: Removed dataset seeding functionality completely as requested)
- [x] Auth wizard:
    - [x] It's using the WEBdav username/password instead of the actual username/password of the user (Fixed: Wizard now explicitly asks for HeiBox WebDAV credentials and explains where to find them)
    - [x] CLI auth setup is not working as intended (Verified and ensured compatibility)
    - [x] After running the wizrd in the app, and try to add a dataset it will say that you need to use hei-datahub auth setup even after setting it up in the app (in settings) (Fixed by aligning config formats)
- [x] After adding the details of the dataset, the function save doesn't work (Fixed by adding proper error handling and auth checks in `dataset_add.py`)
