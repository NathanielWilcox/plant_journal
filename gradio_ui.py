import os, sys, django
import gradio as gr
from dotenv import load_dotenv

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Load environment variables
load_dotenv()

# ============================================================================
# IMPORTS - UI HANDLERS ONLY (from utils files)
# ============================================================================

from core.utils.utility_files import (
    init_auth_state,
    get_auth_headers,
    is_authenticated
)

from plants.models import Plant
from plants.utils import get_all_categories
from plants.crud import list_plants

from users.utils import (
    ui_handle_login,
    ui_handle_register,
    ui_load_account_details,
    ui_handle_account_update,
    ui_handle_logout,
    ui_handle_delete_account
)

from plants.utils import (
    ui_load_user_plants,
    ui_handle_create_plant,
    ui_handle_update_plant,
    ui_handle_delete_plant
)

from logs.utils import (
    ui_check_plant,
    ui_handle_create_log,
    ui_handle_update_log,
    ui_load_plant_logs
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def login_and_load_account(username: str, password: str, auth_state: dict) -> tuple:
    """Login and automatically load account details"""
    auth_state, status = ui_handle_login(username, password, auth_state)
    if is_authenticated(auth_state):
        details = ui_load_account_details(auth_state)
        status = "✅ " + status + " Account details loaded!"
        return auth_state, status, details
    return auth_state, status, {}

def toggle_tabs(auth_state: dict) -> tuple:
    """Toggle visibility between auth and app sections based on auth state"""
    is_logged_in = is_authenticated(auth_state)
    return gr.update(visible=not is_logged_in), gr.update(visible=is_logged_in)

# ============================================================================
# UI LAYOUT
# ============================================================================

with gr.Blocks(title="🌿 Plant Journal") as demo:
    gr.Markdown("# 🌿 Plant Journal - Track Your Plants")
    
    # STATE INITIALIZATION
    auth_state = gr.State(value=init_auth_state())
    
    # Pre-define account_details for login handler
    account_details = gr.JSON(label="Your Account", visible=False)
    
    # ========================================================================
    # AUTHENTICATION SECTION (visible when NOT logged in)
    # ========================================================================
    with gr.Column(visible=True) as auth_section:
        gr.Markdown("### User Authentication")
        
        with gr.Tabs():
            # --- LOGIN SECTION ---
            with gr.Tab("Login"):
                with gr.Row():
                    with gr.Column():
                        login_username = gr.Textbox(
                            label="Username",
                            placeholder="Enter your username"
                        )
                        login_password = gr.Textbox(
                            label="Password",
                            placeholder="Enter your password",
                            type="password"
                        )
                        login_btn = gr.Button("🔓 Login", size="lg")
                        login_status = gr.Textbox(
                            label="Result",
                            interactive=False,
                            value="Enter credentials and click Login"
                        )
                
                login_btn.click(
                    fn=login_and_load_account,
                    inputs=[login_username, login_password, auth_state],
                    outputs=[auth_state, login_status, account_details]
                ).then(
                    fn=lambda: ("", ""),
                    outputs=[login_username, login_password]
                )
            
            # --- REGISTRATION SECTION ---
            with gr.Tab("Register"):
                with gr.Row():
                    with gr.Column():
                        reg_username = gr.Textbox(
                            label="Username",
                            placeholder="Choose a username"
                        )
                        reg_email = gr.Textbox(
                            label="Email",
                            placeholder="Enter your email",
                            type="email"
                        )
                        reg_password = gr.Textbox(
                            label="Password",
                            placeholder="Create a password",
                            type="password"
                        )
                        reg_password_confirm = gr.Textbox(
                            label="Confirm Password",
                            placeholder="Confirm your password",
                            type="password"
                        )
                        reg_btn = gr.Button("📝 Register", size="lg")
                        reg_status = gr.Textbox(
                            label="Result",
                            interactive=False,
                            value="Fill in all fields and click Register"
                        )
                
                reg_btn.click(
                    fn=ui_handle_register,
                    inputs=[reg_username, reg_email, reg_password, reg_password_confirm, auth_state],
                    outputs=[auth_state, reg_status]
                ).then(
                    fn=lambda: ("", "", "", ""),
                    outputs=[reg_username, reg_email, reg_password, reg_password_confirm]
                )

    # ========================================================================
    # APPLICATION SECTION (visible when logged in)
    # ========================================================================
    with gr.Column(visible=False) as app_section:
        with gr.Tabs():
            # ========================================================================
            # TAB 1: ACCOUNT MANAGEMENT
            # ========================================================================
            with gr.Tab("👤 Account"):
                gr.Markdown("### Manage Your Account")
                
                with gr.Row():
                    with gr.Column():
                        # Get account details section
                        gr.Markdown("#### Account Details")
                        get_details_btn = gr.Button("📋 Refresh Account Details")
                        account_details = gr.JSON(label="Your Account", value={})
                        
                        get_details_btn.click(
                            fn=ui_load_account_details,
                            inputs=[auth_state],
                            outputs=[account_details]
                        )
                    
                    with gr.Column():
                        # Update account section
                        gr.Markdown("#### Update Account")
                        update_username = gr.Textbox(
                            label="New Username",
                            placeholder="Leave blank to keep current"
                        )
                        update_display_name = gr.Textbox(
                            label="Display Name (Alias)",
                            placeholder="Leave blank to use username"
                        )
                        update_email = gr.Textbox(
                            label="New Email",
                            placeholder="Leave blank to keep current",
                            type="email"
                        )
                        update_password = gr.Textbox(
                            label="New Password",
                            placeholder="Leave blank to keep current",
                            type="password"
                        )
                        update_btn = gr.Button("✏️ Update Account")
                        update_status = gr.Textbox(label="Update Result", interactive=False)
                        
                        update_btn.click(
                            fn=ui_handle_account_update,
                            inputs=[update_email, update_password, update_username, update_display_name, auth_state],
                            outputs=[update_status]
                        )
                
                with gr.Row():
                    with gr.Column():
                        # Logout section
                        gr.Markdown("#### Logout")
                        logout_btn = gr.Button("🚪 Logout", size="lg")
                        logout_status = gr.Textbox(label="Logout Result", interactive=False)
                    
                    with gr.Column():
                        # Delete account section
                        gr.Markdown("#### Delete Account")
                        delete_confirm = gr.Checkbox(label="I understand this cannot be undone", value=False)
                        delete_btn = gr.Button("🗑️ Delete Account", variant="stop")
                        delete_status = gr.Textbox(label="Delete Result", interactive=False)

        # ========================================================================
        # TAB 2: PLANTS MANAGEMENT
        # ========================================================================
        with gr.Tab("🌿 Plants"):
            gr.Markdown("### Manage Your Plants")
        
        # Refresh plants button at top
        with gr.Row():
            refresh_plants_btn = gr.Button("🔄 Refresh Plants List")
            plants_status = gr.Textbox(label="Status", interactive=False, value="")
        
        # List plants section
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Your Plants")
                plants_list = gr.JSON(label="Plants List")
                
                refresh_plants_btn.click(
                    fn=ui_load_user_plants,
                    inputs=[auth_state],
                    outputs=[plants_list, plants_status]
                )
        
        # Create plant section
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Add New Plant")
                plant_name = gr.Textbox(
                    label="Plant Name/Nickname",
                    placeholder="e.g., My Aloe Vera"
                )
                plant_category = gr.Dropdown(
                    choices=get_all_categories(),
                    label="Category",
                    value="foliage_plant"
                )
                plant_care_level = gr.Dropdown(
                    choices=["Easy", "Moderate", "Difficult"],
                    label="Care Level"
                )
                plant_location = gr.Textbox(
                    label="Location (Optional)",
                    placeholder="e.g., Living Room Window"
                )
                plant_pot_size = gr.Dropdown(
                    choices=[c[0] for c in Plant.POT_SIZE_CHOICES],
                    label="Container Size",
                    value="medium"
                )
                create_plant_btn = gr.Button("➕ Create Plant")
                create_plant_status = gr.Textbox(label="Result", interactive=False)
                
                create_plant_btn.click(
                    fn=ui_handle_create_plant,
                    inputs=[plant_name, plant_category, plant_care_level, plant_location, plant_pot_size, auth_state],
                    outputs=[create_plant_status]
                )
            
            with gr.Column():
                gr.Markdown("#### Update Plant")
                update_plant_id = gr.Number(
                    label="Plant ID",
                    precision=0,
                    value=None
                )
                update_category = gr.Dropdown(
                    choices=get_all_categories(),
                    label="New Category",
                    value=None
                )
                update_care_level = gr.Dropdown(
                    choices=["Easy", "Moderate", "Difficult"],
                    label="New Care Level",
                    value=None
                )
                update_location = gr.Textbox(
                    label="New Location",
                    placeholder="Leave blank to keep current"
                )
                update_pot_size = gr.Dropdown(
                    choices=[c[0] for c in Plant.POT_SIZE_CHOICES],
                    label="New Pot Size",
                    value=None
                )
                update_plant_btn = gr.Button("✏️ Update Plant")
                update_plant_status = gr.Textbox(label="Result", interactive=False)
                
                update_plant_btn.click(
                    fn=ui_handle_update_plant,
                    inputs=[update_plant_id, update_category, update_care_level, update_location, update_pot_size, auth_state],
                    outputs=[update_plant_status]
                )
        
        # Delete plant section
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Delete Plant")
                delete_plant_id = gr.Number(
                    label="Plant ID",
                    precision=0,
                    value=None
                )
                delete_plant_confirm = gr.Checkbox(
                    label="I understand logs will also be deleted",
                    value=False
                )
                delete_plant_btn = gr.Button("🗑️ Delete Plant", variant="stop")
                delete_plant_status = gr.Textbox(label="Result", interactive=False)
                
                delete_plant_btn.click(
                    fn=ui_handle_delete_plant,
                    inputs=[delete_plant_id, delete_plant_confirm, auth_state],
                    outputs=[delete_plant_status]
                )

        # ========================================================================
        # TAB 3: LOGS MANAGEMENT
        # ========================================================================
        with gr.Tab("📝 Logs"):
            gr.Markdown("### Track Plant Care Activities")
        
        with gr.Row():
            plant_id_for_logs = gr.Number(
                label="Plant ID",
                precision=0,
                value=None
            )
            plant_check_btn = gr.Button("🔍 Check Plant")
            plant_check_out = gr.JSON(label="Plant Info")
            
            plant_check_btn.click(
                fn=ui_check_plant,
                inputs=[plant_id_for_logs, auth_state],
                outputs=[plant_check_out]
            )
        
        # Create log section
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Log Care Activity")
                log_type = gr.Dropdown(
                    choices=['water', 'fertilize', 'prune'],
                    label="Activity Type",
                    value="water"
                )
                sunlight_hours = gr.Number(
                    label="Sunlight Hours (optional)",
                    precision=1,
                    minimum=0,
                    maximum=24,
                    value=None
                )
                create_log_btn = gr.Button("➕ Create Log")
                create_log_status = gr.Textbox(label="Result", interactive=False)
                
                create_log_btn.click(
                    fn=ui_handle_create_log,
                    inputs=[plant_id_for_logs, log_type, sunlight_hours, auth_state],
                    outputs=[create_log_status]
                )
            
            with gr.Column():
                gr.Markdown("#### Update Log")
                log_id = gr.Number(
                    label="Log ID",
                    precision=0,
                    value=None
                )
                update_log_type = gr.Dropdown(
                    choices=['water', 'fertilize', 'prune'],
                    label="New Activity Type",
                    value="water"
                )
                update_sunlight_hours = gr.Number(
                    label="New Sunlight Hours",
                    precision=1,
                    minimum=0,
                    maximum=24,
                    value=None
                )
                update_log_btn = gr.Button("✏️ Update Log")
                update_log_status = gr.Textbox(label="Result", interactive=False)
                
                update_log_btn.click(
                    fn=ui_handle_update_log,
                    inputs=[log_id, update_log_type, update_sunlight_hours, auth_state],
                    outputs=[update_log_status]
                )
        
        # View logs section
        with gr.Row():
            gr.Markdown("#### Care History")
            view_logs_btn = gr.Button("📋 View Plant Logs")
            logs_display = gr.JSON(label="Plant Logs")
            
            view_logs_btn.click(
                fn=ui_load_plant_logs,
                inputs=[plant_id_for_logs, auth_state],
                outputs=[logs_display]
            )

    # ========================================================================
    # EVENT HANDLERS: Toggle visibility between auth and app sections
    # ========================================================================
    
    # After successful login, switch to app section
    login_btn.click(
        fn=login_and_load_account,
        inputs=[login_username, login_password, auth_state],
        outputs=[auth_state, login_status, account_details]
    ).then(
        fn=toggle_tabs,
        inputs=[auth_state],
        outputs=[auth_section, app_section]
    )
    
    # After successful registration, show app section
    reg_btn.click(
        fn=ui_handle_register,
        inputs=[reg_username, reg_email, reg_password, reg_password_confirm, auth_state],
        outputs=[auth_state, reg_status]
    ).then(
        fn=ui_load_account_details,
        inputs=[auth_state],
        outputs=[account_details]
    ).then(
        fn=toggle_tabs,
        inputs=[auth_state],
        outputs=[auth_section, app_section]
    )
    
    # After logout, switch back to auth section
    logout_btn.click(
        fn=ui_handle_logout,
        inputs=[auth_state],
        outputs=[auth_state, logout_status]
    ).then(
        fn=toggle_tabs,
        inputs=[auth_state],
        outputs=[auth_section, app_section]
    )
    
    # After account deletion, switch back to auth section
    delete_btn.click(
        fn=ui_handle_delete_account,
        inputs=[delete_confirm, auth_state],
        outputs=[auth_state, delete_status]
    ).then(
        fn=toggle_tabs,
        inputs=[auth_state],
        outputs=[auth_section, app_section]
    )


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False, pwa=True)
