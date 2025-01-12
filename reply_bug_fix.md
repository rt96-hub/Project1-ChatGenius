# Plan of Action to Fix Message Reply Issue

1. **Verify the WebSocket Event Type**  
   - [ ] In the frontend code (e.g., ChatArea or ConnectionContext), when sending a message that is a reply, confirm the WebSocket event type is correctly indicating a reply.  
   - [ ] Compare the actual event sent:
     [CODE START]
     {type: 'new_message', channel_id: 4, content: 'reply message', parent_id: 1295, parent: {...}}
     [CODE END]
     with what should be sent according to the docs in backend/api_docs.md or how the backend’s main.py expects a “reply”-specific event.

2. **Check the Endpoint Used for Replies**  
   - [ ] Look at the endpoint usage in ChatArea. For replies, the correct endpoint should be:
     [CODE START]
     POST /channels/{channel_id}/messages/{parent_id}/reply
     [CODE END]
   - [ ] Confirm that when a user replies, the code calls the above endpoint rather than the regular:
     [CODE START]
     POST /channels/{channel_id}/messages
     [CODE END]
   - [ ] If the code is sending a WebSocket message with `type: 'new_message'` and not leveraging `parent_id` properly on the server side, update the code to either:
     - Use a different message type (like "reply_message") and update the backend to handle it, or
     - Make sure the server triggers the reply logic upon detecting `parent_id`.

3. **Update the Backend WebSocket Handler**  
   - [ ] In backend/main.py or equivalent, review the “if event_type == 'new_message'” branch:
     [CODE START]
     if event_type == "new_message":
         # ...
         # Missing logic to treat parent_id as a reply?
     [CODE END]
   - [ ] Ensure it calls the reply logic (e.g., create_reply) if `parent_id` is not null, or confirm that we’re using the separate route that handles replies.

4. **Validate Broadcasting of Reply Events**  
   - [ ] In main.py’s create_message_reply_endpoint, note how the server broadcasts:
     [CODE START]
     "type": "message_created",
     "message": { ... }
     [CODE END]
     or similarly “new_message”. Confirm the event is consistent with the frontend’s expectations for replies.

5. **Test the End-to-End Flow**  
   - [ ] Reply to a message in the UI and check the console/network logs to see if:
     - The correct endpoint is called (`/reply`).
     - The WebSocket event includes `parent_id` and is processed as a reply on the server.
   - [ ] Confirm the UI receives the “message_created” or “new_message” event with `parent_id` present, placing it in the proper reply chain.

6. **Refactor & Document**  
   - [ ] Once fixed, refactor the code to reduce confusion between normal messages and replies (e.g., use consistent naming).  
   - [ ] Update documentation (frontend_docs.md and any relevant client-side code) to clarify that replies use a separate endpoint and may require a different WebSocket event.
