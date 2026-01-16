# 0.64-beta

## TO ADD
- [ ] Add support for MacOS - Probably will stick to uv install for beta and then will do the homebrew install later
- [ ] Add shortcut to naviguate to the left/right h/l

## TO CHANGE
- [!] Combine Spatial coverage and resolution into "spatial info" and temporal coverage and resolution into "temporal info" in the data table only, when i add/show/edit the dataset i want to add them seperatly.

## TO FIX
- [ ] Data won't appear after setting up auth, it will apear just after launching the app again
- [!] Fix the scroll, it feels weird and not smooth - (wasn't fixed, it added the scrollbar back)

## ADDED/CHANGED/FIXED
- [x] Add a copy minimalistic btn for non-technical people, for example at the start of each field in the dataset details
- [x] Add a feature where when you are in dataset details, you can press multiple keys to copy different fields, for example ctrl+c r e f (VIM like)
- [x] Add a dynamic footer for the Yank shortcut in the dataset details

- [x] Change the layout of the columns in the dataset table
- [x] Remove the generate ID field, just generate it automatically based on the title
- [x] If the Any of the fields were left empty, just put "Not specified"
- [x] Make the category not required

- [x] Fix the shortcut `o` in the dataset detail page where it tries to open the source instead of the link from Acess/Location and remove copy url
- [x] Fix the issue when on Windows I press `Shift+Ctrl+S` the setting doesn't appear
- [x] The dataset is not changing when i saved/delete until i re-launch the app
- [x] There is a weird box or rectangle above the show/hide additional metadata in add dataset
- [x] Fix the layout of the edit dataset, it's not centered
- [x] Fix the issue where i open the dataset and i go back again the it's not focused on the one that i open, it starts all over again
- [x] Fix the issue where I press `esc` after searching it will take me to the main page (i want to click `esc` it will take me to the search above and then when i click `esc` again it will take me to the home page)
- [x] Fix the issue where you press `Ctrl+T`(not just theme, but when i press `esc` and i get the prompt to close the app or not, I press `esc` again and it takes me to home without the focus on search) on the home page for theme selection and when you select, the focus on the search bar will disapear, so basicaly there are `home` and `search` with the same layout and different footer, one it focues on the search bar, and the other doesn't
- [x] Fix the issue where when i search and click on the dataset and i go back the search will undo (it will give me all the data)
