# Plan of Action

- [ ] **Review WebSocket Implementation on the Backend**

  - Examine the event broadcasting functions in `backend/app/routers/messages.py`, specifically functions that should broadcast new messages to clients via WebSockets.
  
  - Verify that after a new message is created, the server is correctly broadcasting the event to connected clients.

- [ ] **Check Event Broadcasting Functions**

  - Analyze the `events` module used for broadcasting messages.
  
  - Ensure that the functions `broadcast_message_created` and related event handlers are being called properly after a message is created or updated.

- [ ] **Verify WebSocket Connections in the Frontend**

  - Confirm that the frontend clients establish WebSocket connections to receive real-time updates.
  
  - Check that clients are listening for events related to new messages and updating the UI accordingly.

- [ ] **Analyze Client-Side Event Handlers**

  - Review the code that handles incoming WebSocket events on the client side.
  
  - Ensure that upon receiving a new message event, the client updates the message list and renders the new message.

- [ ] **Identify Possible Issues**

  - If the backend is not broadcasting events, investigate why:

    - The event broadcasting functions might not be called after a message is created.

    - There could be an issue with the event system configuration.

  - If the frontend is not receiving events, check for:

    - WebSocket connection issues.

    - Incorrect event handling or missing event listeners.

- [ ] **Test and Debug**

  - **Backend Debugging:**

    - Add logging statements to the backend to confirm that event broadcasting functions are executed.

      - Example in `backend/events_manager.py`:

        [CODE START]
        import logging
        logger = logging.getLogger(__name__)

        async def broadcast_message_created(channel_id, message, current_user):
            logger.info(f"Broadcasting new message to channel {channel_id}")
            # Existing broadcasting logic...
        [CODE END]

    - Monitor logs to verify that messages are broadcasted when a new message is created.

  - **Frontend Debugging:**

    - Use browser developer tools to inspect WebSocket connections and incoming messages.

    - Verify that the client receives the new message events.

- [ ] **Implement Fixes**

  - **Backend Fixes:**

    - If event broadcasting functions are not called, ensure they are invoked after message creation.

      - In `create_message_endpoint` of `backend/app/routers/messages.py`, after creating a message, add:

        [CODE START]
        # After creating the message
        await events.broadcast_message_created(channel_id, db_message, current_user)
        [CODE END]

  - **Frontend Fixes:**

    - If the client is not handling incoming events, add or correct event listeners.

      - In the frontend WebSocket handling code, ensure there is a listener for new message events:

        [CODE START]
        socket.on('message_created', (message) => {
          // Update the message list with the new message
        });
        [CODE END]

- [ ] **Update Documentation**

  - **READING MD DOCS**

    - Review `backend/api_docs.md` for existing documentation on message events and WebSocket endpoints.

  - **WRITING MD DOCS**

    - Update `backend/api_docs.md` to include:

      - Information about the message broadcasting mechanism.

      - Details of the events emitted (e.g., `message_created`, `message_updated`).

      - Formats of the events and sample data structures.

    - Document any changes made to the backend or frontend that affect how real-time messaging operates.
