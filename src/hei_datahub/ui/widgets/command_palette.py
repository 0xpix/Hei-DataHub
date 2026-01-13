import re
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, OptionList
from textual.widgets.option_list import Option
import inspect

class CustomCommandPalette(ModalScreen[str]):
    """A custom command palette replacing the default one."""

    CSS = """
    CustomCommandPalette {
        align: center middle;
        background: rgba(0, 0, 0, 0.5);
    }

    #command-palette-container {
        width: 60;
        height: 20;
        background: $surface;
        border: wide $primary;
        padding: 1;
    }

    #command-input {
        border: none;
        background: $surface;
        color: $text;
        width: 100%;
        margin-bottom: 1;
        dock: top;
    }

    #command-list {
        height: 1fr;
        border: none;
        background: $surface;
        scrollbar-gutter: stable;
    }

    OptionList:focus {
        border: none;
    }

    .category-header {
        background: $primary 20%;
        color: $accent;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("down", "cursor_down", "Next", show=False),
        Binding("up", "cursor_up", "Previous", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="command-palette-container"):
            yield Input(placeholder="> Search commands...", id="command-input")
            yield OptionList(id="command-list")

    def on_mount(self) -> None:
        self.query_one(Input).focus()
        self._load_commands()

    def action_cursor_down(self) -> None:
        self.query_one(OptionList).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(OptionList).action_cursor_up()

    def _load_commands(self) -> None:
        """Load available commands from the active screen and app."""
        self.commands = []

        # 1. Get the screen that is BEHIND this modal
        target_screen = None
        if len(self.app.screen_stack) >= 2:
            target_screen = self.app.screen_stack[-2]
        else:
            # Fallback
            target_screen = self.app.screen

        found_bindings = {} # Label -> Action

        # Helper to add commands
        def add_command(name, action, description, key=None):
            label = description
            if key:
                label = f"{description} ({key})"
            # Prefer existing binding description if we already have it
            # Also, check if this action is already added to avoid DuplicateID
            if label not in found_bindings:
                found_bindings[label] = action

        # 1. Collect from bindings (High priority) - ONLY SHORTCUTS
        if target_screen:
            try:
                # active_bindings returns dict[str, ActiveBinding]
                # Filter duplicates (e.g. from both App and Screen)
                for active_binding in target_screen.active_bindings.values():
                    binding = active_binding.binding
                    if binding.description and binding.show:
                        add_command(binding.action, binding.action, binding.description, binding.key)
            except Exception:
                pass

        # NOTE: Removed collection of unbound actions from App and Screen
        # per user request to only show "shortcuts not the commands"

        # Add a special entry for Theme if not present (sometimes it might not appear if binding is overshadowed)
        if "Change Theme (ctrl+t)" not in found_bindings:
            # Check if App has it bound
            pass

        for label, action in found_bindings.items():
            self.commands.append((label, action))

        # Sort commands alphabetically by label
        self.commands.sort(key=lambda x: x[0])

        self._update_list(self.commands, show_categories=True)

    def _get_category(self, action: str) -> str:
        """Infer category from action name."""
        # Check if action is likely a system/app one
        if action in ["quit", "bell", "toggle_dark"]:
            return "System"

        if "." in action:
            category = action.split(".")[0]
            if category == "screen":
                 return "Screen"
            return category.title()

        # Try to guess based on source?
        return "General"

    def _update_list(self, commands, show_categories: bool = False) -> None:
        option_list = self.query_one(OptionList)
        option_list.clear_options()

        if not commands:
            option_list.add_option(Option(prompt="No results found", disabled=True))
            return

        first_selectable_index = None
        current_index = 0

        # Track added IDs to prevent duplicates within the list update
        added_ids = set()

        if show_categories:
            # Group by category
            categories = {}
            for label, action in commands:
                cat = self._get_category(action)
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append((label, action))

            # Sort categories
            sorted_cats = sorted(categories.keys())

            for cat in sorted_cats:
                # Add Header
                header_id = f"cat_{cat}"
                if header_id not in added_ids:
                    header_text = f"── {cat} ──"
                    option_list.add_option(Option(prompt=header_text, disabled=True, id=header_id))
                    added_ids.add(header_id)
                    current_index += 1

                # Add items
                for label, action in categories[cat]:
                    # Ensure we don't add duplicate action IDs in the OptionList
                    # Textual OptionList doesn't allow duplicate IDs.
                    # If we have same action but different labels, we need unique IDs.
                    # Since we keyed found_bindings by Label, the Labels are unique, but Actions might be same?
                    # Actually valid commands usually have unique Actions.
                    # But if an action appears multiple times (e.g. same action, different label), we need to handle it.
                    # Here we have list of (label, action).

                    # Construct a unique ID if needed, or just skip if exactly same action is already there?
                    # The traceback happened because "opencode" action was added twice?
                    # No, likely because we were doing blindly.

                    # We will rely on unique IDs. If action is duplicated, append suffix
                    option_id = action
                    counter = 1
                    while option_id in added_ids:
                        option_id = f"{action}_{counter}"
                        counter += 1

                    option_list.add_option(Option(prompt=f"  {label}", id=option_id))
                    added_ids.add(option_id)

                    if first_selectable_index is None:
                        first_selectable_index = current_index
                    current_index += 1
        else:
            # Flat list
            for label, action in commands:
                option_id = action
                counter = 1
                while option_id in added_ids:
                    option_id = f"{action}_{counter}"
                    counter += 1

                option_list.add_option(Option(prompt=label, id=option_id))
                added_ids.add(option_id)

                if first_selectable_index is None:
                    first_selectable_index = current_index
                current_index += 1

        if first_selectable_index is not None:
            option_list.highlighted = first_selectable_index

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.lower()
        if not query:
            self._update_list(self.commands, show_categories=True)
            return

        filtered = []
        for label, action in self.commands:
            # Match against label or action or category
            cat = self._get_category(action).lower()
            if (query in label.lower()) or (query in action.lower()) or (query in cat):
                filtered.append((label, action))

        # Always show categories
        self._update_list(filtered, show_categories=True)

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        option_list = self.query_one(OptionList)
        idx = option_list.highlighted
        if idx is not None:
             try:
                 option = option_list.get_option_at_index(idx)
                 if not option.disabled and option.id and not option.id.startswith("cat_"):
                     action = option.id
                     import re
                     real_action = re.sub(r'_\d+$', '', action)
                     self.dismiss(result=real_action)
             except Exception:
                 pass

    @on(OptionList.OptionSelected)
    def on_option_selected(self, event: OptionList.OptionSelected) -> None:
        action = event.option_id
        if action and not action.startswith("cat_"):
            import re
            real_action = re.sub(r'_\d+$', '', action)
            self.dismiss(result=real_action)

    def action_close(self) -> None:
        self.dismiss(result=None)
