# Channel Joining Feature Update Plan

## Overview
This document outlines the necessary changes to remove the current invite code system and implement new channel joining features.

## Database Changes
- [ ] Remove `join_code` column from `Channel` model in `models.py`
- [ ] Create and run Alembic migration to remove the column
- [ ] Update channel creation and update schemas in `schemas.py` to remove join_code field
- [ ] Update `ChannelCreate` and `ChannelUpdate` Pydantic models to remove join_code field

## API Endpoint Changes
- [ ] Remove `/channels/{channel_id}/join-code` endpoint from `main.py`
- [ ] Remove `/channels/join/{join_code}` endpoint from `main.py`
- [ ] Remove `/channels/{channel_id}/invite` endpoint from `main.py`
- [ ] Update channel creation endpoint to remove join code generation
- [ ] Update channel update endpoint to remove join code handling
- [ ] Update `/channels/{channel_id}/privacy` endpoint to remove join_code field from request/response
- [ ] Update channel response models to remove join_code field

## CRUD Operations
- [ ] Remove `generate_join_code()` function from `crud.py`
- [ ] Remove `get_channel_by_join_code()` function from `crud.py`
- [ ] Update `create_channel()` function to remove join code generation
- [ ] Update `update_channel()` function to remove join code handling
- [ ] Remove any join code validation logic from channel operations
- [ ] Update `update_channel_privacy()` function to remove join code handling

## WebSocket Events
- [ ] Remove join code related events from WebSocket notifications
- [ ] Update channel update event payload to remove join code field
- [ ] Update channel created event payload to remove join code field
- [ ] Update channel privacy change event to remove join code field

## Documentation Updates
- [ ] Update API documentation to remove join code related endpoints
- [ ] Update backend documentation to reflect new channel joining flow
- [ ] Remove join code references from schema documentation
- [ ] Update WebSocket event documentation to remove join code fields
- [ ] Update channel privacy documentation to remove join code references

## Testing
- [ ] Remove join code related test cases from channel tests
- [ ] Update channel creation/update test cases to reflect new structure
- [ ] Update integration tests to remove join code scenarios
- [ ] Update WebSocket event tests to remove join code fields
- [ ] Update channel privacy test cases to remove join code testing

## Security Considerations
- [ ] Review and update channel access control logic
- [ ] Ensure private channels remain secure without join codes
- [ ] Update role-based access control for channel joining
- [ ] Review and update channel privacy validation logic
- [ ] Add additional security checks for channel joining without invite codes

## Frontend Implications
Note: These changes will require corresponding frontend updates
- [ ] Remove join code UI elements
- [ ] Update channel creation/edit forms
- [ ] Update channel joining flow
- [ ] Update error handling for removed endpoints
- [ ] Remove join code related components and utilities
- [ ] Update channel privacy settings UI
- [ ] Update WebSocket event handlers to handle updated payloads

## Migration Plan
- [ ] Create script to handle existing channels with join codes
- [ ] Plan for backward compatibility during deployment
- [ ] Document migration steps for deployment
- [ ] Create database backup before migration
- [ ] Test migration process in staging environment
- [ ] Plan rollback strategy if needed

## Future Considerations
- Consider implementing alternative channel discovery mechanisms
- Plan for channel invitation system if needed
- Consider implementing channel categories or tags for discovery
- Consider implementing channel moderation tools
- Plan for scalability of new joining mechanism 

## Frontend Changes

### Component Updates

#### Sidebar Component
- [ ] Remove join code generation button/functionality
- [ ] Update channel list items to remove join code displays
- [ ] Modify channel creation flow in CreateChannelModal
- [ ] Update ConfirmDialog for new joining flow

#### ChatArea Component
- [ ] Update ChannelHeader to remove join code display/copy functionality
- [ ] Modify ChannelSettingsModal to remove join code settings
- [ ] Update MembersList component for new joining permissions

#### Modal Components
- [ ] Remove any join code input fields from channel creation forms
- [ ] Update channel settings forms to remove join code sections
- [ ] Modify channel joining confirmation dialogs
- [ ] Update error messages and validation related to join codes

### Type Definitions (`types/`)
- [ ] Update Channel interface to remove joinCode field
- [ ] Modify ChannelCreation type to remove join code
- [ ] Update ChannelUpdate type to remove join code
- [ ] Revise WebSocket event types for channel updates

### API Integration (`hooks/`)
- [ ] Update useChannel hook to remove join code functionality
- [ ] Modify useChannelCreate hook to remove join code generation
- [ ] Update useChannelUpdate hook to remove join code handling
- [ ] Remove join code related API calls from useChannelJoin hook

### Context Updates (`contexts/`)
- [ ] Update ChannelContext to remove join code state
- [ ] Modify channel-related actions in context
- [ ] Update WebSocket event handlers in ConnectionContext
- [ ] Remove join code related state management

### Utility Functions (`utils/`)
- [ ] Remove join code validation functions
- [ ] Update channel permission checking utilities
- [ ] Modify channel creation/update helpers
- [ ] Update WebSocket message handlers

### State Management
- [ ] Remove join code from channel state
- [ ] Update channel creation/update forms state
- [ ] Modify channel list state management
- [ ] Update error handling state for removed functionality

### UI/UX Updates
- [ ] Remove join code copy/paste functionality
- [ ] Update channel joining user interface
- [ ] Modify channel settings interface
- [ ] Update error messages and tooltips
- [ ] Revise channel creation workflow
- [ ] Update channel privacy indicators

### Testing Updates
- [ ] Update component tests to remove join code scenarios
- [ ] Modify integration tests for new joining flow
- [ ] Update context/hook tests
- [ ] Revise utility function tests
- [ ] Update mock data to remove join code fields

### Documentation Updates
- [ ] Update component documentation
- [ ] Revise hook documentation
- [ ] Update context documentation
- [ ] Modify utility function documentation
- [ ] Update type definition documentation
- [ ] Revise development guidelines

### Build and Configuration
- [ ] Update any environment variables related to join codes
- [ ] Modify TypeScript types in tsconfig
- [ ] Update any relevant Next.js configurations
- [ ] Review and update package dependencies

### Performance Considerations
- [ ] Review and optimize new channel joining flow
- [ ] Update component rendering optimizations
- [ ] Modify WebSocket event handling efficiency
- [ ] Review and update error boundary handling 