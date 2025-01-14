# Modularization Plan: Files and Endpoints






Below is a proposed plan detailing each file to be created or updated, and which endpoints or CRUD functions should reside in each. We also list the relevant WebSocket endpoints. Use checkboxes to track your progress.

---

## 1. Files and Endpoints

[x] **Routers Folder**  
Create a new folder named "routers" to hold the various route files.

[x] **routers/auth.py**  
This file will contain the Auth0-related login and verification endpoints. From @main.py and @auth0.py, move or create the following endpoints here:

[CODE START]
@router.post("/auth/sync") => sync_auth0_user_endpoint  
@router.get("/auth/verify") => verify_auth_endpoint (if you have one)
[CODE END]

[x] **routers/users.py**  
Move the user profile endpoints from @main.py into this file:

[CODE START]
@router.put("/users/me/bio") => update_user_bio  
@router.put("/users/me/name") => update_user_name  
@router.get("/users/me") => get_current_user_data (if needed)
[CODE END]

[x] **routers/channels.py**  
Move the channel endpoints from @main.py into this file:

[CODE START]
@router.post("/channels/") => create_channel_endpoint  
@router.get("/channels/me") => read_user_channels  
@router.get("/channels/available") => read_available_channels  
@router.post("/channels/{channel_id}/join") => join_channel_endpoint (if desired)
[CODE END]

[x] **routers/files.py**  
Take the routes from @file_uploads.py and place them here:

[CODE START]
@router.post("/files/upload") => upload_file  
@router.get("/files/{file_id}/download-url") => get_download_url  
@router.delete("/files/{file_id}") => delete_file
[CODE END]

[x] **routers/search.py**  
Keep or move the routes already in @search.py here:

[CODE START]
@router.get("/search/messages") => search_messages  
@router.get("/search/users") => search_users  
@router.get("/search/channels") => search_channels  
@router.get("/search/files") => search_files
[CODE END]

[x] **routers/messages.py**  
Keep or move the routes already in @main.py here:
[CODE START]
@router.post("/channels/{channel_id}/messages") => create_message_endpoint  
@router.get("/channels/{channel_id}/messages") => get_channel_messages  
@router.get("/channels/{channel_id}/messages/{message_id}") => get_message  
@router.put("/channels/{channel_id}/messages/{message_id}") => update_message  
@router.delete("/channels/{channel_id}/messages/{message_id}") => delete_message
@router.post("/channels/{channel_id}/messages/{message_id}/reply") => create_message_reply_endpoint
@router.get("/channels/{channel_id}/messages/{message_id}/reply-chain") => get_message_reply_chain_endpoint
@router.post("/channels/{channel_id}/messages/with-file") => create_message_with_file_endpoint
@router.post("/channels/{channel_id}/messages/{message_id}/reply-with-file") => create_reply_with_file_endpoint
[CODE END]

[x] **routers/reactions.py**  
Keep or move the routes already in @main.py here:
[CODE START]
@router.get("/reactions/") => list_reactions  
@router.post("/channels/{channel_id}/messages/{message_id}/reactions") => add_reaction_endpoint  
@router.delete("/channels/{channel_id}/messages/{message_id}/reactions/{reaction_id}") => remove_reaction_endpoint
[CODE END]

[x] **routers/websockets.py**  
Move the WebSocket endpoint from @main.py to this file:

[CODE START]
@router.websocket("/ws") => websocket_endpoint
[CODE END]

This file will handle all real-time communication. If you have separate domain-specific WebSocket events, consider splitting them further in the future.

---

## 2. CRUD File Splits

Create a "crud" folder to hold domain-specific CRUD files:

[x] **crud/users.py**  
[CODE START]
get_user  
get_user_by_email  
get_user_by_auth0_id  
create_personal_channel  
sync_auth0_user  
update_user_bio  
update_user_name  
[CODE END]

[x] **crud/channels.py**  
[CODE START]
create_channel  
get_channel  
get_user_channels  
update_channel  
delete_channel  
get_channel_members  
remove_channel_member  
update_channel_privacy  
join_channel  
leave_channel  
get_available_channels
[CODE END]

[x] **crud/messages.py**  
[CODE START]
get_message  
create_message => (If you have a create_message function)  
create_reply => (If you have a create_reply function)  
get_message_reply_chain  
[CODE END]

[x] **crud/reactions.py**  
[CODE START]
get_all_reactions  
get_reaction  
add_reaction_to_message  
remove_reaction_from_message
[CODE END]

[ ] **crud/files.py** (Optional if you want to separate file logic)  
[CODE START]
(Any create/read/update/delete functions for file uploads)
[CODE END]

You can decide to keep some smaller CRUD operations together (e.g., user_in_channel could remain in crud/channels.py).

---

## 3. WebSocket Functions

Move your WebSocket manager and broadcasting functions (currently in @main.py and possibly in @file_uploads.py) to a dedicated module, for instance:

[ ] **websocket_manager.py** (stay as is or move to a "managers" folder)  
• Functions: connect, broadcast_to_channel, broadcast_file_upload, broadcast_file_deleted, etc.  
• The same logic is already in your code, but just consolidated in one place.

---

## 4. Main File (main.py)

[ ] In the newly refactored main.py:  
• Keep the FastAPI instance initialization.  
• Keep the database setup and middleware setup.  
• Import each router from the "routers" folder and include them with the proper prefixes.  
• Example:
[CODE START]
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
...
app.include_router(websockets.router, tags=["websockets"])
[CODE END]

This ensures that each route is cleanly separated into its respective domain file.

---

## Progress Summary

- [x] Create and move endpoints to routers/auth.py  
- [x] Create and move endpoints to routers/users.py  
- [x] Create and move endpoints to routers/channels.py  
- [x] Create and move endpoints to routers/files.py  
- [x] Create and move endpoints to routers/search.py  
- [x] Create and move endpoints to routers/reactions.py  
- [x] Create and move WebSocket endpoint to routers/websockets.py  
- [x] Split CRUD functions across crud/users.py, crud/channels.py, crud/messages.py, crud/reactions.py (and optionally crud/files.py)  
- [ ] Clean up main.py to only include initialization and router inclusion  

This modular approach will help organize your code and make it easier to scale and maintain.