---
name: VIP Custom Billing UI Help Text
overview: Add contextual help text and update field labels in the billing UI within the AOP iFrame for VIP Custom orders. Changes include updating field names based on deal type (Direct/Partner Fulfillment/2-tier), and adding blue warning labels with hover text to guide sales agents in providing correct PO numbers and Bill To information.
todos:
  - id: update_po_required_label
    content: Update 'PO Required' checkbox label to 'PO Number Required on Invoice' in PaymentCardDialog when IS_CONVERT_TO_ORDER_FLOW() is true
    status: pending
  - id: update_po_number_label_partner
    content: Change 'PO Number' to 'Partner PO Number' for Partner Fulfillment deals in PaymentCardDialog
    status: pending
  - id: update_po_upload_label
    content: Change 'Partner PO upload file (PDF)' to 'Partner PO Upload (PDF)' for Partner Fulfillment deals
    status: pending
  - id: add_partner_po_warning
    content: Add blue warning label with hover text when PO number is entered for Partner Fulfillment deals
    status: pending
    dependencies:
      - update_po_number_label_partner
  - id: update_reseller_label
    content: Change 'Reseller' to 'Reseller ID' for 2-tier Partner Fulfillment deals
    status: pending
  - id: add_reseller_warning
    content: Add blue warning label with hover text for Reseller ID in 2-tier Partner Fulfillment deals
    status: pending
    dependencies:
      - update_reseller_label
  - id: add_billto_warning
    content: Add blue warning label with hover text in Bill To Contacts section for Direct orders in PartnerCardDialog
    status: pending
isProject: false
---

# VIP Custom Billing UI Help Text Implementation

## Overview

Add contextual help text and update field labels in the Payment Details section of the AOP iFrame to reduce PO number and Bill To contact errors when placing VIP Custom orders.

## Context

- All changes apply when `IS_CONVERT_TO_ORDER_FLOW()` is true (AOP iFrame context)
- Deal types: Direct (`IS_PARTNER_DIRECT(partnerName)`), Partner Fulfillment (`!IS_PARTNER_DIRECT(partnerName)`), 2-tier Partner Fulfillment (`!IS_PARTNER_DIRECT(partnerName) && tier === 2`)

## Files to Modify

### 1. `client/src/components/Partners/components/PaymentCardDialog.js`

Main payment dialog component where all Payment Details fields are rendered.

**Changes:**

- **Requirement #1**: Update "PO Required" checkbox label to "PO Number Required on Invoice" or "PO # Required on Invoice" (for both Direct and Partner Fulfillment)
- **Requirement #2**: For Partner Fulfillment deals:
- Change "PO Number" field label to "Partner PO Number"
- Change "Partner PO upload file (PDF)" to "Partner PO Upload (PDF)"
- Add blue warning label when PO number is entered with hover text: "The Partner PO Number must match the uploaded file to bill and invoice this order"
- **Requirement #3**: For 2-tier Partner Fulfillment deals:
- Apply all Partner Fulfillment changes above
- Change "Reseller" field label to "Reseller ID"
- Add blue warning label for Reseller ID with hover text: "Reseller ID is required for 2 Tier Partner fulfillment"

### 2. `client/src/components/Partners/components/PartnerCardDialog.js`

Bill To contact dialog component.

**Changes:**

- **Requirement #4**: For Direct orders only, add blue warning label in Bill To Contacts section with hover text: "Please confirm this is the correct contact for invoicing. This cannot be changed after the order is placed."

## Implementation Details

### Field Label Updates

- Use conditional rendering based on `IS_CONVERT_TO_ORDER_FLOW()` to show updated labels
- Check deal type using `IS_PARTNER_DIRECT(props.partnerName)` and `props.tier`

### Warning Labels

- Use Spectrum `Alert` component with `variant="info"` for blue warning labels
- Use `OverlayTrigger` with `Tooltip` for hover text (similar pattern to existing `_renderPaymentMessage()`)
- Warning labels should appear:
- After PO number is entered (Partner Fulfillment)
- When Reseller ID field is visible (2-tier)
- In Bill To Contacts section (Direct orders)

### Message Display Strategy

- If multiple messages exist in the same section, display them vertically stacked
- Ensure messages don't truncate or break workflow
- Use existing CSS classes for consistent styling

## Technical Approach

1. **Conditional Label Rendering**: Update `_renderPONumberInput()`, `_renderPoPdfUpload()`, `_renderResellerInput()`, and `_renderPORequired()` methods to conditionally show updated labels when `IS_CONVERT_TO_ORDER_FLOW()` is true
2. **Warning Label Components**: Create helper methods:

- `_renderPartnerPOWarning()` - Shows when PO number is entered for Partner Fulfillment
- `_renderResellerIDWarning()` - Shows for 2-tier Partner Fulfillment
- Add warning in `PartnerCardDialog` for Bill To contacts (Direct only)

1. **Deal Type Detection**:

- Direct: `IS_PARTNER_DIRECT(props.partnerName) === true`
- Partner Fulfillment: `IS_PARTNER_DIRECT(props.partnerName) === false`
- 2-tier Partner Fulfillment: `IS_PARTNER_DIRECT(props.partnerName) === false && parseInt(props.tier) === 2`

## Testing Considerations

- Verify labels update correctly for each deal type
- Ensure warning labels appear at appropriate times
- Confirm hover text displays correctly
- Test that multiple messages don't overlap or truncate
- Validate no impact on existing quoting/ordering workflow

