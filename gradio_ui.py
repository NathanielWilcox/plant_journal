import os, sys, django
from unicodedata import category
import gradio as gr
from dotenv import load_dotenv
from core.utils.utility_files import api_request
from core.auth.token_validator import token_validator
from core.auth.decorators import with_auth_retry
from core.settings import API_BASE_URL

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Now we can import Django models
from plants.models import Plant
from plants.utils import (
    get_plant_template,
    handle_update,
    load_plant_templates,
    get_all_categories,
    get_category_placeholder,
    update_care_info
)
from plants.crud import (
    create_plant,
    update_plant,
    delete_plant,
    list_plants
)
from logs.crud import (
    create_log,
    update_log,
    # delete_log,
    list_logs,
    list_logs_for_plant
)
from logs.utils import (
    check_plant_exists,
    search_plant_issues,
    normalize_log_data,
    get_log_types
    )
from users.crud import (
    register_user,
    update_user,
    delete_user,
    list_users
)
from users.utils import (
    login_user,
    get_user_account_details,
    register_user,
    update_user_account,
    logout_user,
    delete_user_account
)

API_BASE_URL = os.getenv("API_BASE_URL")

# Load environment variables
load_dotenv()

# Gradio UI
with gr.Blocks() as demo:

    with gr.Tab("Login"):
        gr.Markdown("### 🔐 User Authentication")

        username = gr.Textbox(label="Username", placeholder="Enter your username")
        password = gr.Textbox(label="Password", placeholder="Enter your password", type="password")
        login_btn = gr.Button("Login")
        login_out = gr.JSON(label="Login Result")

        def handle_login(username, password):
            return login_user(username, password)

        login_btn.click(
            fn=handle_login,
            inputs=[username, password],
            outputs=login_out
        )

    with gr.Tab("Account"):
        gr.Markdown("### 🧑 Manage Account")

        # --- Row 1: Get account details ---
        with gr.Row():
            token = gr.Textbox(label="JWT Token", placeholder="Enter your JWT token", type="password")
            get_details_btn = gr.Button("Get Account Details")
            details_out = gr.JSON(label="Account Details")

            get_details_btn.click(
                fn=get_user_account_details,
                inputs=[token],
                outputs=details_out
            )

        # --- Row 2: Update account ---
        with gr.Row():
            update_email = gr.Textbox(label="New Email", placeholder="Enter new email")
            update_password = gr.Textbox(label="New Password", placeholder="Enter new password", type="password")
            update_btn = gr.Button("Update Account")
            update_out = gr.JSON(label="Update Result")

            def handle_account_update(token, email, password):
                update_data = {}
                if email:
                    update_data['email'] = email
                if password:
                    update_data['password'] = password
                return update_user_account(token, update_data)

            update_btn.click(
                fn=handle_account_update,
                inputs=[token, update_email, update_password],
                outputs=update_out
            )
        # --- Row 3: Delete account ---
        with gr.Row():
            del_token = gr.Textbox(label="JWT Token", placeholder="Enter your JWT token", type="password")
            del_btn = gr.Button("Delete Account")
            del_out = gr.JSON(label="Delete Result")

            del_btn.click(
                fn=delete_user_account,
                inputs=[del_token],
                outputs=del_out
            )
        
        # --- Row 4: Logout ---
        with gr.Row():
            logout_token = gr.Textbox(label="JWT Token", placeholder="Enter your JWT token", type="password")
            logout_btn = gr.Button("Logout")
            logout_out = gr.JSON(label="Logout Result")

            logout_btn.click(
                fn=logout_user,
                inputs=[logout_token],
                outputs=logout_out
            )
    
    with gr.Tab("Plants"):
        gr.Markdown("### 🌿 Manage Plants")

        # --- Row 1: List all plants ---
        with gr.Row():
            list_btn = gr.Button("📋 List Plants")
            list_out = gr.JSON()
            list_btn.click(list_plants, outputs=list_out)

        # --- Row 2: Create plant ---
        with gr.Row():
            with gr.Column():
                name = gr.Textbox(label="Plant Name/Nickname", placeholder="e.g., My Aloe")

                category_dropdown = gr.Dropdown(
                    choices=[c[0] for c in Plant.CATEGORY_CHOICES],
                    label="Category"
                )

                care_level = gr.Dropdown(
                    label="Care Level",
                    choices=["Easy", "Moderate", "Difficult"],
                    value=None,
                    allow_custom_value=False
                )
                location = gr.Textbox(label="Location (Optional)")
                pot_size = gr.Dropdown(
                    choices=[c[0] for c in Plant.POT_SIZE_CHOICES],
                    value="medium",
                    label="Container Size"
                )

                create_btn = gr.Button("Create Plant")
                result_out = gr.JSON(label="Result")

                def update_care_info_ui(category):
                    care_info = update_care_info(category)
                    return care_info['watering_schedule'], care_info['sunlight_preference']

                def handle_create(name, category, care_level, location, pot_size):
                    return create_plant(
                        name=name,
                        category=category,
                        care_level=care_level,
                        location=location,
                        pot_size=pot_size
                    )
                
                create_btn.click(
                    fn=handle_create,
                    inputs=[name, category_dropdown, care_level, location, pot_size],
                    outputs=result_out
                )
            

        # --- Row 3: Update plant ---
        with gr.Row():
            pid = gr.Number(label="Plant ID")

            upd_category = gr.Dropdown(
                choices=get_all_categories(),
                label="Updated Category",
                value=None
            )

            care_level_upd = gr.Dropdown(
                choices=["Easy", "Moderate", "Difficult"],
                label="Updated Care Level",
                value=None,
                allow_custom_value=False
            )

            location_upd = gr.Textbox(label="Enter Location")

            pot_size_upd = gr.Dropdown(
                choices=[c[0] for c in Plant.POT_SIZE_CHOICES],
                label="Updated Pot Size",
                value=None
            )

            update_btn = gr.Button("✏️ Update Plant")

            update_btn.click(
                fn=handle_update,
                inputs=[pid, upd_category, care_level_upd, location_upd, pot_size_upd],
                outputs=gr.Textbox(label="Update Result")   # or gr.JSON() if you want raw API response
            )

            def handle_update(pid, category, care_level, location, pot_size):
                return update_plant(
                    plant_id=pid,
                    category=category,
                    care_level=care_level,
                    location=location,
                    pot_size=pot_size
                )



        # --- Row 4: Delete plant ---
        with gr.Row():
            del_pid = gr.Number(label="Plant ID")
            del_btn = gr.Button("🗑️ Delete Plant")
            del_out = gr.JSON()
            del_btn.click(delete_plant, inputs=[del_pid], outputs=del_out)

    with gr.Tab("Logs"):
        gr.Markdown("### Manage Logs for a Plant")

        # --- Plant Selection + Validation ---
        with gr.Row():
            plant_id = gr.Number(label="Plant ID", interactive=True)
            plant_check_out = gr.JSON(label="Plant Check")

            plant_id.change(
            check_plant_exists,
            inputs=[plant_id],
            outputs=[plant_check_out]
        )

        # --- Log Creation ---
        with gr.Row():
            log_type = gr.Dropdown(
                choices=['water', 'fertilize', 'prune', 'health_issue'],
                label="Log Type"
            )
            sunlight_hours = gr.Number(label="Sunlight Hours (optional)", precision=1)
            # TODO: Create dynamic health issues dropdown based on existing issues, also create existing issues
            selected_issue = gr.Dropdown(label="Select Health Issue", choices=[], visible=False, value=None)

            create_log_btn = gr.Button("Create Log")
            create_log_out = gr.JSON(label="Result")

            # Show health issues dropdown if log_type is 'health_issue'
            def toggle_health_issue_dropdown(log_type_value):
                return gr.update(visible=(log_type_value == 'health_issue'))
            
            log_type.change(
                toggle_health_issue_dropdown,
                inputs=[log_type],
                outputs=[selected_issue]
            )

            create_log_btn.click(
                create_log,
                inputs=[plant_id, log_type, sunlight_hours, selected_issue],
                outputs=[create_log_out]
            )

        # --- Update Logs ---
        with gr.Row():
            lid = gr.Number(label="Log ID")
            update_log_type = gr.Dropdown(
                choices=['water', 'fertilize', 'prune', 'health_issue'],
                label="Log Type"
            )
            update_water_amount = gr.Number(label="Water Amount (ml)", precision=0)
            update_sunlight_hours = gr.Number(label="Sunlight Hours", precision=1)
            update_log_btn = gr.Button("✏️ Update Log")
            update_log_out = gr.JSON()

            update_log_btn.click(
                update_log,
                inputs=[lid, update_log_type, update_water_amount, update_sunlight_hours],
                outputs=update_log_out
            )

        # # --- Delete Logs ---
        # with gr.Row():
        #     del_lid = gr.Number(label="Log ID")
        #     del_log_btn = gr.Button("🗑️ Delete Log")
        #     del_log_out = gr.JSON()
        #     del_log_btn.click(delete_log, inputs=del_lid, outputs=del_log_out)

    
    

demo.launch(server_name="127.0.0.1", server_port=7860)
